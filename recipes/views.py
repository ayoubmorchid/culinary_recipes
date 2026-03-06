from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from .models import Recipe, Category, Comment, Rating
from .forms import RecipeForm, CommentForm, RatingForm, SearchForm
from favorites.models import Favorite


def home(request):
    """
    Vue de la page d'accueil.
    Affiche les dernières recettes et les mieux notées.
    """
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
    """
    Vue liste de toutes les recettes publiées.
    Inclut la pagination et les options de tri.
    """
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 9

    def get_queryset(self):
        queryset = Recipe.objects.filter(is_published=True).select_related(
            'author', 'category'
        ).prefetch_related('ratings')

        sort_by = (self.request.GET.get('sort_by') or '-created_at').strip()

        # Tri sécurisé
        if sort_by == 'average_rating':
            queryset = queryset.annotate(
                avg_rating=Avg('ratings__rating')
            ).order_by('-avg_rating', '-created_at')
        elif sort_by == 'preparation_time':
            queryset = queryset.order_by('preparation_time', '-created_at')
        else:
            # empêcher order_by('') أو قيم غريبة
            allowed = {'-created_at', 'created_at', 'title', '-title'}
            if sort_by not in allowed:
                sort_by = '-created_at'
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['sort_by'] = self.request.GET.get('sort_by', '-created_at')
        return context


class RecipeDetailView(DetailView):
    """
    Vue détail d'une recette.
    Affiche toutes les informations, commentaires et notes.
    """
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


def search_recipes(request):
    """
    Recherche avancée sécurisée (évite order_by('') et champs inconnus).
    """
    form = SearchForm(request.GET)
    recipes = Recipe.objects.filter(is_published=True).select_related(
        'author', 'category'
    ).prefetch_related('ratings')

    # mapping sécurisé للتري
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'title': 'title',
        'title_desc': '-title',
        'preparation_time': 'preparation_time',
        'preparation_time_desc': '-preparation_time',
    }

    if form.is_valid():
        query = (form.cleaned_data.get('query') or '').strip()
        category = form.cleaned_data.get('category')
        max_time = form.cleaned_data.get('max_preparation_time')
        sort_by = (form.cleaned_data.get('sort_by') or '').strip()

        if query:
            recipes = recipes.filter(
                Q(title__icontains=query) |
                Q(ingredients__icontains=query) |
                Q(description__icontains=query)
            )

        if category:
            recipes = recipes.filter(category=category)

        if max_time is not None:
            recipes = recipes.filter(preparation_time__lte=max_time)

        if sort_by == 'average_rating':
            recipes = recipes.annotate(
                avg_rating=Avg('ratings__rating')
            ).order_by('-avg_rating', '-created_at')
        else:
            order_field = sort_map.get(sort_by, '-created_at')  # default آمن
            recipes = recipes.order_by(order_field)

    paginator = Paginator(recipes, 9)
    page = request.GET.get('page')
    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)

    context = {
        'form': form,
        'recipes': recipes,
        'categories': Category.objects.all(),
    }
    return render(request, 'recipes/search.html', context)


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