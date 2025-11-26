import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import Chat, TextMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f"chat_{self.chat_id}"

        # Проверка входа пользователя
        user = self.scope["user"]
        if user is None or isinstance(user, AnonymousUser):
            await self.close()
            return

        # Проверка: пользователь участник этого чата
        try:
            chat = await self.get_chat()
            if user.id not in [chat.user1_id, chat.user2_id]:
                await self.close()
                return
        except Chat.DoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"]

        # Сохранить сообщение
        await self.save_message(user, message)

        # Разослать обоим участникам чата
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "user": user.username,
                "message": message,
            }
        )

    async def chat_message(self, event):
        await self.send(json.dumps({
            "user": event["user"],
            "message": event["message"],
        }))

    @database_sync_to_async
    def get_chat(self):
        return Chat.objects.get(id=self.chat_id)

    @database_sync_to_async
    def save_message(self, user, message):
        return TextMessage.objects.create(
            chat_id=self.chat_id,
            sender=user,
            content=message
        )
