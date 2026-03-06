from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    """
    Modèle de catégorie de recettes.
    Permet d'organiser les recettes par type (Entrées, Plats, Desserts, etc.)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Nom de la catégorie')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug URL')
    description = models.TextField(blank=True, verbose_name='Description')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes:category', kwargs={'slug': self.slug})

    @property
    def recipe_count(self):
        """Retourne le nombre de recettes dans cette catégorie."""
        return self.recipes.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    """
    Modèle principal de recette de cuisine.
    Contient toutes les informations nécessaires pour décrire une recette.
    """
    title = models.CharField(max_length=200, verbose_name='Titre de la recette')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug URL')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Auteur'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Catégorie'
    )
    description = models.TextField(verbose_name='Description courte')
    ingredients = models.TextField(verbose_name='Ingrédients')
    instructions = models.TextField(verbose_name='Instructions de préparation')
    preparation_time = models.PositiveIntegerField(
        default=0,
        verbose_name='Temps de préparation (minutes)'
    )
    cooking_time = models.PositiveIntegerField(
        default=0,
        verbose_name='Temps de cuisson (minutes)'
    )
    servings = models.PositiveIntegerField(
        default=4,
        verbose_name='Nombre de personnes'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        verbose_name='Image de la recette'
    )
    is_published = models.BooleanField(default=True, verbose_name='Publiée')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Recette'
        verbose_name_plural = 'Recettes'
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_time(self):
        """Retourne le temps total de préparation."""
        return self.preparation_time + self.cooking_time

    @property
    def average_rating(self):
        """Calcule la note moyenne de la recette."""
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 1)
        return 0

    @property
    def total_ratings(self):
        """Retourne le nombre total de notes."""
        return self.ratings.count()

    @property
    def total_comments(self):
        """Retourne le nombre total de commentaires."""
        return self.comments.count()


class Rating(models.Model):
    """
    Modèle de notation des recettes.
    Chaque utilisateur peut noter une recette une seule fois (1-5 étoiles).
    """
    RATING_CHOICES = [
        (1, '1 ★'),
        (2, '2 ★★★'),
        (3, '3 ★★★'),
        (4, '4 ★★★★'),
        (5, '5 ★★★★★'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Recette'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Utilisateur'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name='Note')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        unique_together = ('recipe', 'user')
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title} - {self.rating}★"


class Comment(models.Model):
    """
    Modèle de commentaires sur les recettes.
    Les utilisateurs connectés peuvent commenter les recettes.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Recette'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Auteur'
    )
    content = models.TextField(verbose_name='Commentaire')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True, verbose_name='Approuvé')

    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ('-created_at',)

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.recipe.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
