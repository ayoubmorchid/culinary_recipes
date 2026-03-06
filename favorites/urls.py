from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('', views.favorite_recipes, name='favorites_list'),
    path('ajouter/<int:recipe_id>/', views.add_to_favorites, name='add_favorite'),
    path('supprimer/<int:recipe_id>/', views.remove_from_favorites, name='remove_favorite'),
]
