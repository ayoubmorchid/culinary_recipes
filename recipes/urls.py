from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),

    # Liste des recettes
    path('recettes/', views.RecipeListView.as_view(), name='recipe_list'),

    # Création d'une recette  ✅ لازم قبل slug
    path('recette/creer/', views.RecipeCreateView.as_view(), name='recipe_create'),

    # Mes recettes
    path('mes-recettes/', views.my_recipes, name='my_recipes'),



    # Recettes par catégorie
    path('categorie/<slug:slug>/', views.CategoryRecipeListView.as_view(), name='category'),

    # Modification d'une recette ✅ قبل detail
    path('recette/<slug:slug>/modifier/', views.RecipeUpdateView.as_view(), name='recipe_update'),

    # Suppression d'une recette ✅ قبل detail
    path('recette/<slug:slug>/supprimer/', views.RecipeDeleteView.as_view(), name='recipe_delete'),

    # Détail d'une recette ✅ خليها آخر وحدة
    path('recette/<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
]