from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    position = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name='Должность'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='Телефон'
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # Убедитесь, что app_label не переопределен

    def __str__(self):
        return self.username

