from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Modèle de profil utilisateur étendu.
    Chaque utilisateur possède un profil avec une bio et une photo.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biographie')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    def __str__(self):
        return f'Profil de {self.user.username}'
