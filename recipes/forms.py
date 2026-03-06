from django import forms
from .models import Recipe, Comment, Rating, Category


class RecipeForm(forms.ModelForm):
    """
    Formulaire de création et modification d'une recette.
    """
    class Meta:
        model = Recipe
        fields = [
            'title', 'category', 'description', 'ingredients', 'instructions',
            'preparation_time', 'cooking_time', 'servings', 'image', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la recette'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Courte description de la recette'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Liste des ingrédients (un par ligne)'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Étapes de préparation'
            }),
            'preparation_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Minutes'
            }),
            'cooking_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Minutes'
            }),
            'servings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Nombre de personnes'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_ingredients(self):
        """Valide et formatte les ingrédients."""
        ingredients = self.cleaned_data.get('ingredients', '')
        if not ingredients:
            raise forms.ValidationError("Les ingrédients sont obligatoires.")
        return ingredients

    def clean_instructions(self):
        """Valide les instructions."""
        instructions = self.cleaned_data.get('instructions', '')
        if not instructions:
            raise forms.ValidationError("Les instructions sont obligatoires.")
        return instructions


class CommentForm(forms.ModelForm):
    """
    Formulaire de commentaire sur une recette.
    """
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Écrivez votre commentaire...'
            })
        }

    def clean_content(self):
        """Valide le contenu du commentaire."""
        content = self.cleaned_data.get('content', '')
        if not content.strip():
            raise forms.ValidationError("Le commentaire ne peut pas être vide.")
        if len(content) < 3:
            raise forms.ValidationError("Le commentaire doit contenir au moins 3 caractères.")
        return content


class RatingForm(forms.ModelForm):
    """
    Formulaire de notation d'une recette.
    """
    class Meta:
        model = Rating
        fields = ('rating',)
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }


class SearchForm(forms.Form):
    """
    Formulaire de recherche avancée de recettes.
    """
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une recette...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    max_preparation_time = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Temps max (minutes)'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('created_at', 'Plus récentes'),
            ('-created_at', 'Plus anciennes'),
            ('average_rating', 'Mieux notées'),
            ('preparation_time', 'Temps de préparation'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
