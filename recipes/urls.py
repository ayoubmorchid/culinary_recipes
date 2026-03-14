from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [

    # liste recettes
    path('', views.RecipeListView.as_view(), name='recipe_list'),

    # page recherche
    path('recherche/', views.search_recipes, name='search'),

    # créer recette
    path('creer/', views.RecipeCreateView.as_view(), name='recipe_create'),

    # mes recettes
    path('mes-recettes/', views.my_recipes, name='my_recipes'),

    # recettes par catégorie
    path('categorie/<slug:slug>/', views.CategoryRecipeListView.as_view(), name='category'),

    # modifier
    path('<slug:slug>/modifier/', views.RecipeUpdateView.as_view(), name='recipe_update'),

    # supprimer
    path('<slug:slug>/supprimer/', views.RecipeDeleteView.as_view(), name='recipe_delete'),

    # detail
    path('<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
]