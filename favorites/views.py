from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .models import Favorite
from recipes.models import Recipe


@login_required
def favorite_recipes(request):
    """
    Vue des recettes favorites de l'utilisateur connecté.
    """
    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('recipe__author', 'recipe__category').order_by('-created_at')

    # Pagination
    paginator = Paginator(favorites, 9)
    page = request.GET.get('page')

    try:
        favorites = paginator.page(page)
    except PageNotAnInteger:
        favorites = paginator.page(1)
    except EmptyPage:
        favorites = paginator.page(paginator.num_pages)

    context = {
        'favorites': favorites,
        'title': 'Mes recettes favorites'
    }
    return render(request, 'favorites/favorites_list.html', context)


@login_required
def add_to_favorites(request, recipe_id):
    """
    Vue pour ajouter une recette aux favoris.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id, is_published=True)

    # Vérifier si déjà favori
    if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
        messages.info(request, 'Cette recette est déjà dans vos favoris.')
    else:
        Favorite.objects.create(user=request.user, recipe=recipe)
        messages.success(request, f'"{recipe.title}" a été ajouté à vos favoris!')

    return redirect(recipe.get_absolute_url())


@login_required
def remove_from_favorites(request, recipe_id):
    """
    Vue pour supprimer une recette des favoris.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id, is_published=True)

    favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
    if favorite.exists():
        favorite.delete()
        messages.success(request, f'"{recipe.title}" a été retiré de vos favoris!')
    else:
        messages.warning(request, 'Cette recette n\'est pas dans vos favoris.')

    # Rediriger vers la page des favoris ou la recette
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('favorites:favorites_list')
