from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from .models import Recipe, Category, Comment, Rating
from .forms import RecipeForm, CommentForm, RatingForm
from favorites.models import Favorite

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from accounts.models import Profile


def home(request):
    latest_recipes = Recipe.objects.filter(
        is_published=True
    ).select_related('author', 'category').order_by('-created_at')[:6]

    top_rated_recipes = Recipe.objects.filter(
        is_published=True
    ).annotate(
        avg_rating=Avg('ratings__rating')
    ).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating', '-created_at')[:6]

    categories = Category.objects.all()

    context = {
        'latest_recipes': latest_recipes,
        'top_rated_recipes': top_rated_recipes,
        'categories': categories,
    }
    return render(request, 'recipes/home.html', context)


class RecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 9

    def get_queryset(self):
        queryset = Recipe.objects.all().select_related(
            'author', 'category'
        ).prefetch_related('ratings')

        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(title__istartswith=query)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

    def get_queryset(self):
        return Recipe.objects.select_related(
            'author', 'category'
        ).prefetch_related('comments__author', 'ratings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()

        comments = recipe.comments.filter(is_approved=True).select_related('author')
        context['comments'] = comments

        if self.request.user.is_authenticated:
            context['comment_form'] = CommentForm()

            user_rating = recipe.ratings.filter(user=self.request.user).first()
            context['rating_form'] = RatingForm(instance=user_rating)
            context['user_rating'] = user_rating

            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user,
                recipe=recipe
            ).exists()

        context['similar_recipes'] = Recipe.objects.filter(
            category=recipe.category,
            is_published=True
        ).exclude(pk=recipe.pk)[:3]

        return context

    def post(self, request, *args, **kwargs):
        recipe = self.get_object()

        if 'comment_submit' in request.POST:
            if not request.user.is_authenticated:
                messages.warning(request, 'Vous devez être connecté pour commenter.')
                return redirect('accounts:login')

            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.recipe = recipe
                comment.author = request.user
                comment.save()
                messages.success(request, 'Votre commentaire a été ajouté!')
                return redirect(recipe.get_absolute_url())

        elif 'rating_submit' in request.POST:
            if not request.user.is_authenticated:
                messages.warning(request, 'Vous devez être connecté pour noter.')
                return redirect('accounts:login')

            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                Rating.objects.update_or_create(
                    user=request.user,
                    recipe=recipe,
                    defaults={'rating': rating_form.cleaned_data['rating']}
                )
                messages.success(request, 'Votre note a été enregistrée!')
                return redirect(recipe.get_absolute_url())

        return redirect(recipe.get_absolute_url())


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Recette créée avec succès!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Créer une recette'
        return context


class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author

    def form_valid(self, form):
        messages.success(self.request, 'Recette mise à jour avec succès!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Modifier la recette'
        return context


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    template_name = 'recipes/recipe_delete.html'
    success_url = reverse_lazy('recipes:recipe_list')

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Recette supprimée avec succès!')
        return super().delete(request, *args, **kwargs)


class CategoryRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/category_recipes.html'
    context_object_name = 'recipes'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Recipe.objects.filter(
            category=self.category,
            is_published=True
        ).select_related('author', 'category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context


@login_required(login_url='accounts:login')
def my_recipes(request):
    recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(recipes, 9)
    page = request.GET.get('page')

    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)

    context = {
        'recipes': recipes,
        'title': 'Mes recettes'
    }
    return render(request, 'recipes/my_recipes.html', context)


@staff_member_required(login_url='accounts:login')
def dashboard(request):
    """
    Admin dashboard showing key statistics and recent activity.
    """
    User = get_user_model()
    
    context = {
        'total_users': User.objects.count(),
        'total_recipes': Recipe.objects.count(),
        'total_categories': Category.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_favorites': Favorite.objects.count(),
        'last_users': User.objects.select_related('profile').order_by('-date_joined')[:5],
        'last_recipes': Recipe.objects.select_related('author__profile', 'category').order_by('-created_at')[:5],
    }
    
    return render(request, 'recipes/dashboard.html', context)
