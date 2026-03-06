from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les profils utilisateurs.
    """
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'bio')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
