from django.contrib.auth.models import AbstractUser
from django.db import models
from .crypto.aes import decrypt_message
# Create your models here.

class MessengerUser(AbstractUser):

    birthday = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    status = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True)

    def __str__(self):
        return self.username


class Chat(models.Model):
    # user1 = models.ForeignKey(MessengerUser, on_delete=models.CASCADE, related_name='user1')
    # user2 = models.ForeignKey(MessengerUser, on_delete=models.CASCADE, related_name='user2')

    name = models.CharField(max_length=150, default="Chat", verbose_name="Название чата")

    users = models.ManyToManyField(MessengerUser)

    date_of_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}"

    def has_participant(self, user):
        if user is None or getattr(user, "pk", None) is None:
            return False
        user_pk = user.pk
        return any(participant.pk == user_pk for participant in self.users.all())

    def get_companion(self, user):
        if user is None or getattr(user, "pk", None) is None:
            return None
        user_pk = user.pk
        for participant in self.users.all():
            if participant.pk != user_pk:
                return participant
        return None
    
    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class TextMessage(models.Model):
    content = models.TextField()
    date_of_sending = models.DateTimeField(auto_now_add=True)  # уже исправили раньше
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')  # ← добавь related_name
    sender = models.ForeignKey(MessengerUser, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    iv = models.CharField(max_length=32)

    def __str__(self):
        return self.content[:50]

    def decrypt_content(self):
        return decrypt_message(self.content, self.iv)

    class Meta:
        ordering = ['date_of_sending']
        verbose_name = 'Текстовое сообщение'
        verbose_name_plural = 'Текстовые сообщения'