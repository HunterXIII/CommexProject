import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

from .models import Chat, TextMessage
from .crypto.aes import encrypt_message, decrypt_message


class ChatConsumer(AsyncWebsocketConsumer):
    """Обрабатывает WebSocket-соединения для обмена сообщениями в чатах."""

    async def connect(self):
        """Подключает пользователя к группе чата после проверки прав."""
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.group_name = f"chat_{self.chat_id}"
        self.user = self.scope["user"]

        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close()
            return

        chat = await self.get_chat()
        if not chat or not await self.is_user_in_chat(chat):
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        """Исключает пользователя из группы при разрыве соединения."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Определяет тип действия и вызывает нужный обработчик."""
        data = json.loads(text_data)
        action = data.get("type")

        if action == "send_message":
            await self.handle_send(data)

        elif action == "delete_message":
            await self.handle_delete(data)

        elif action == "read_message":
            await self.handle_read(data)



    async def handle_send(self, data):
        """Сохраняет новое сообщение и рассылает его участникам чата."""
        text = data.get("message", "").strip()
        if not text:
            return

        msg = await self.save_message(text)
        decrypted = decrypt_message(msg.content, msg.iv)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "ws_message_created",
                "message_id": msg.id,
                "user": self.user.username,
                "message": decrypted,  # ✅ ВАЖНО
                "time": msg.date_of_sending.strftime("%H:%M"),
                "is_read": False,
            }
        )

    async def handle_delete(self, data):
        """Удаляет сообщение, если запрос инициировал его автор."""
        msg_id = data.get("message_id")
        msg = await self.get_message(msg_id)

        if msg and msg.sender_id == self.user.id:
            await self.delete_message(msg_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "ws_message_deleted",
                    "message_id": msg_id,
                }
            )

    async def handle_read(self, data):
        """Помечает сообщение прочитанным и синхронизирует статус."""
        msg_id = data.get("message_id")
        updated = await self.mark_as_read(msg_id)

        if updated:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "ws_message_read",
                    "message_id": msg_id,
                }
            )

    async def ws_message_created(self, event):
        """Отправляет клиенту данные о новом сообщении."""
        await self.send(json.dumps({
            "event": "message_created",
            "message_id": event["message_id"],
            "user": event["user"],
            "message": event["message"],
            "time": event["time"],
            "is_read": event["is_read"],
        }))

    async def ws_message_deleted(self, event):
        """Сообщает клиенту об удалении сообщения."""
        await self.send(json.dumps({
            "event": "message_deleted",
            "message_id": event["message_id"],
        }))

    async def ws_message_read(self, event):
        """Уведомляет клиента о смене статуса прочтения."""
        await self.send(json.dumps({
            "event": "message_read",
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def get_chat(self):
        """Возвращает объект чата по идентификатору."""
        return Chat.objects.filter(id=self.chat_id).first()

    @database_sync_to_async
    def is_user_in_chat(self, chat):
        """Проверяет, состоит ли пользователь в чате."""
        return self.user in chat.users.all()

    @database_sync_to_async
    def save_message(self, text):
        """Создаёт зашифрованное сообщение в базе данных."""
        content, iv = encrypt_message(text)
        return TextMessage.objects.create(
            chat_id=self.chat_id,
            sender=self.user,
            content=content,
            iv=iv,
            date_of_sending=now()
        )

    @database_sync_to_async
    def get_message(self, msg_id):
        """Находит сообщение по идентификатору."""
        return TextMessage.objects.filter(id=msg_id).first()

    @database_sync_to_async
    def delete_message(self, msg_id):
        """Удаляет сообщение из базы."""
        TextMessage.objects.filter(id=msg_id).delete()

    @database_sync_to_async
    def mark_as_read(self, msg_id):
        """Помечает сообщение прочитанным, если оно не принадлежит текущему пользователю."""
        return TextMessage.objects.filter(
            id=msg_id,
            is_read=False
        ).exclude(sender=self.user).update(is_read=True)
