from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class MessengerUser(AbstractUser):

    birthday = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    status = models.BooleanField(default=False)
    profile_image = models.ImageField(blank=True)

    def __str__(self):
        return self.username

 