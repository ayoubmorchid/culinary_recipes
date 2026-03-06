from django.db import models
from django.contrib.auth.models import User
from recipes.models import Recipe


class Favorite(models.Model):
    """
    Modèle de favoris.
    Permet aux utilisateurs d'ajouter des recettes à leurs favoris.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Utilisateur'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recette'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoris'
        unique_together = ('user', 'recipe')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"
