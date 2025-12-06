import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import Chat, TextMessage
from django.utils.timezone import now


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f"chat_{self.chat_id}"

        user = self.scope["user"]
        if user is None or isinstance(user, AnonymousUser):
            await self.close()
            return

        # Проверяем участник ли пользователь чата
        chat = await self.get_chat()
        if chat is None:
            await self.close()
            return

        is_participant = await self.is_participant(user.id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message", "")

        user = self.scope["user"]

        # Сохраняем сообщение → получаем message.id
        msg = await self.save_message(user, message_text)

        # Отправляем всем участникам
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "user": user.username,
                "message": message_text,
                "message_id": msg.id,
                "time": msg.date_of_sending.strftime("%H:%M"),
            }
        )

    async def chat_message(self, event):
        await self.send(json.dumps({
            "user": event["user"],
            "message": event["message"],
            "message_id": event["message_id"],
            "time": event["time"],
        }))

    # -------------------------
    # DATABASE OPERATIONS
    # -------------------------

    @database_sync_to_async
    def get_chat(self):
        return Chat.objects.filter(id=self.chat_id).first()

    @database_sync_to_async
    def is_participant(self, user_id):
        return Chat.objects.filter(id=self.chat_id, users__id=user_id).exists()

    @database_sync_to_async
    def save_message(self, user, message):
        return TextMessage.objects.create(
            chat_id=self.chat_id,
            sender=user,
            content=message,
            date_of_sending=now()
        )
