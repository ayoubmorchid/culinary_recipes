from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # Liste des recettes
    path('', views.RecipeListView.as_view(), name='recipe_list'),

    # Recherche
    path('recherche/', views.search_recipes, name='search'),

    # Création d'une recette
    path('creer/', views.RecipeCreateView.as_view(), name='recipe_create'),

    # Mes recettes
    path('mes-recettes/', views.my_recipes, name='my_recipes'),

    # Recettes par catégorie
    path('categorie/<slug:slug>/', views.CategoryRecipeListView.as_view(), name='category'),

    # Modification d'une recette
    path('<slug:slug>/modifier/', views.RecipeUpdateView.as_view(), name='recipe_update'),

    # Suppression d'une recette
    path('<slug:slug>/supprimer/', views.RecipeDeleteView.as_view(), name='recipe_delete'),

    # Détail d'une recette
    path('<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
]