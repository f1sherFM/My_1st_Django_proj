from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Оставляем username для входа, а email делаем уникальным для надежной связи аккаунтов.
    email = models.EmailField("Email", unique=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField("О себе", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Профиль {self.user.username}"
