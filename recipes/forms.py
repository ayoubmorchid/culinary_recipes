from django import forms
from .models import Recipe, Comment, Rating, Category


class RecipeForm(forms.ModelForm):
    """
    Formulaire de création et modification d'une recette.
    """
    class Meta:
        model = Recipe
        fields = [
            'title',
            'category',
            'description',
            'ingredients',
            'instructions',
            'preparation_time',
            'cooking_time',
            'servings',
            'image',
            'is_published'
        ]


class CommentForm(forms.ModelForm):
    """
    Formulaire de commentaire sur une recette.
    """
    class Meta:
        model = Comment
        fields = ('content',)


class RatingForm(forms.ModelForm):
    """
    Formulaire de notation d'une recette.
    """
    class Meta:
        model = Rating
        fields = ('rating',)


class SearchForm(forms.Form):
    """
    Formulaire de recherche avancée de recettes.
    """
    query = forms.CharField(
        max_length=200,
        required=False
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Toutes les catégories"
    )

    max_preparation_time = forms.IntegerField(
        required=False,
        min_value=0
    )

    sort_by = forms.ChoiceField(
        choices=[
            ('created_at', 'Plus récentes'),
            ('-created_at', 'Plus anciennes'),
            ('average_rating', 'Mieux notées'),
            ('preparation_time', 'Temps de préparation'),
        ],
        required=False
    )