from django.contrib import admin
from .models import Recipe, Category, Rating, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les catégories.
    """
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les recettes.
    """
    list_display = ('title', 'author', 'category', 'preparation_time', 'cooking_time', 'is_published', 'created_at')
    list_filter = ('category', 'is_published', 'created_at', 'author')
    search_fields = ('title', 'description', 'ingredients', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'slug', 'author', 'category', 'description')
        }),
        ('Contenu', {
            'fields': ('ingredients', 'instructions', 'image')
        }),
        ('Paramètres', {
            'fields': ('preparation_time', 'cooking_time', 'servings', 'is_published')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les notes.
    """
    list_display = ('recipe', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('recipe__title', 'user__username')
    raw_id_fields = ('recipe', 'user')
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour les commentaires.
    """
    list_display = ('recipe', 'author', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'recipe__title')
    raw_id_fields = ('recipe', 'author')
    ordering = ('-created_at',)
    actions = ['approve_comments', 'disapprove_comments']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Commentaire'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = 'Approuver les commentaires sélectionnés'

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = 'Désapprouver les commentaires sélectionnés'
