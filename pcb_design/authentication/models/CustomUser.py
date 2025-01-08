from django.contrib.auth.models import AbstractUser
from django.db import models
from .CustomUserManager import CustomUserManager


class CustomUser(AbstractUser):  
    username = None
    email = models.EmailField(unique=True)
    is_logged_out = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
