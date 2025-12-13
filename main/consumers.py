import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

from .models import Chat, TextMessage
from django.utils.timezone import now

from .crypto.aes import encrypt_message, decrypt_message
from asgiref.sync import sync_to_async

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
        if chat is None or not await self.is_user_in_chat(user, chat):
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

        msg = await self.save_message(user, message_text)

        decrypted = await self.decrypt_db_message(msg)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "user": user.username,
                "message": decrypted,
                "message_id": msg.id,
                "time": msg.date_of_sending.strftime("%H:%M"),
            }
        )


    async def chat_message(self, event):
        await self.send(json.dumps({
            "event": "message_created", 
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
    def save_message(self, user, message):
        content, iv = encrypt_message(message)
        return TextMessage.objects.create(
            chat_id=self.chat_id,
            sender=user,
            content=content,
            iv=iv,
            date_of_sending=now()
        )

    @database_sync_to_async
    def is_user_in_chat(self, user, chat):
        return user in chat.users.all()

    @sync_to_async
    def decrypt_db_message(self, msg):
        return decrypt_message(msg.content, msg.iv)