# Create your models here.
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('mechanic', 'Mecánico'),
        ('secretary', 'Secretaria'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username