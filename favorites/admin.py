from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les favoris.
    """
    list_display = ('user', 'recipe', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'recipe__title')
    raw_id_fields = ('user', 'recipe')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
