from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class MessengerUser(AbstractUser):

    birthday = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    status = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True)

    def __str__(self):
        return self.username


class Chat(models.Model):
    user1 = models.ForeignKey(MessengerUser, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(MessengerUser, on_delete=models.CASCADE, related_name='user2')
    date_of_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1.username} and {self.user2.username}"

class TextMessage(models.Model):
    content = models.TextField()
    date_of_sending = models.DateTimeField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(MessengerUser, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content
    
    class Meta:
        verbose_name = 'Текстовое сообщение'
        verbose_name_plural = 'Текстовые сообщения'