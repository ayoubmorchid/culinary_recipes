from django import forms
from .models import Recipe, Comment, Rating, Category


class RecipeForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'une recette.
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
            'is_published',
        ]
        labels = {
            'title': 'Titre',
            'category': 'Catégorie',
            'description': 'Description',
            'ingredients': 'Ingrédients',
            'instructions': 'Instructions',
            'preparation_time': 'Temps de préparation',
            'cooking_time': 'Temps de cuisson',
            'servings': 'Portions',
            'image': 'Image',
            'is_published': 'Publier la recette',
        }
        help_texts = {
            'ingredients': 'Saisissez un ingrédient par ligne.',
            'instructions': 'Saisissez une étape par ligne.',
            'preparation_time': 'Durée en minutes.',
            'cooking_time': 'Durée en minutes.',
            'servings': 'Nombre de personnes.',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la recette'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Courte description de la recette'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Ex :\n2 tomates\n1 oignon\n200g de pâtes'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Ex :\n1. Laver les légumes\n2. Couper les tomates\n3. Faire cuire...'
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
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Le titre est obligatoire.")
        if len(title) < 3:
            raise forms.ValidationError("Le titre doit contenir au moins 3 caractères.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise forms.ValidationError("La description est obligatoire.")
        return description

    def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients', '').strip()
        if not ingredients:
            raise forms.ValidationError("Les ingrédients sont obligatoires.")
        return ingredients

    def clean_instructions(self):
        instructions = self.cleaned_data.get('instructions', '').strip()
        if not instructions:
            raise forms.ValidationError("Les instructions sont obligatoires.")
        return instructions

    def clean_preparation_time(self):
        preparation_time = self.cleaned_data.get('preparation_time')
        if preparation_time is not None and preparation_time < 0:
            raise forms.ValidationError("Le temps de préparation ne peut pas être négatif.")
        return preparation_time

    def clean_cooking_time(self):
        cooking_time = self.cleaned_data.get('cooking_time')
        if cooking_time is not None and cooking_time < 0:
            raise forms.ValidationError("Le temps de cuisson ne peut pas être négatif.")
        return cooking_time

    def clean_servings(self):
        servings = self.cleaned_data.get('servings')
        if servings is not None and servings < 1:
            raise forms.ValidationError("Le nombre de portions doit être au moins 1.")
        return servings

    def clean(self):
        cleaned_data = super().clean()
        preparation_time = cleaned_data.get('preparation_time') or 0
        cooking_time = cleaned_data.get('cooking_time') or 0

        if preparation_time == 0 and cooking_time == 0:
            raise forms.ValidationError(
                "Veuillez renseigner au moins un temps de préparation ou de cuisson."
            )

        return cleaned_data


class CommentForm(forms.ModelForm):
    """
    Formulaire de commentaire sur une recette.
    """

    class Meta:
        model = Comment
        fields = ('content',)
        labels = {
            'content': 'Commentaire'
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Écrivez votre commentaire...'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
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
        labels = {
            'rating': 'Note'
        }
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class SearchForm(forms.Form):
    """
    Formulaire de recherche avancée de recettes.
    """

    query = forms.CharField(
        max_length=200,
        required=False,
        label='Recherche',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une recette...'
        })
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="Toutes les catégories",
        label='Catégorie',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    max_preparation_time = forms.IntegerField(
        required=False,
        min_value=0,
        label='Temps max de préparation',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Temps max (minutes)'
        })
    )

    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Plus récentes'),
            ('created_at', 'Plus anciennes'),
            ('-average_rating', 'Mieux notées'),
            ('preparation_time', 'Temps de préparation'),
        ],
        required=False,
        label='Trier par',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all().order_by('name')