from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from recipes.models import Recipe


def register(request):
    """
    Vue d'inscription d'un nouvel utilisateur.
    Crée un nouveau compte et connecte l'utilisateur automatiquement.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Compte créé avec succès! Bienvenue {user.username}!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """
    Vue de connexion utilisateur.
    Authentifie l'utilisateur et crée une session.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'accounts/login.html')


def user_logout(request):
    """
    Vue de déconnexion utilisateur.
    Termine la session en cours.
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')


@login_required
def profile(request):
    """
    Vue du profil utilisateur.
    Affiche les informations du profil et permet sa modification.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    # Récupérer les recettes de l'utilisateur
    user_recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')[:5]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_recipes': user_recipes,
    }
    return render(request, 'accounts/profile.html', context)


class UserProfileView(DetailView):
    """
    Vue publique du profil utilisateur.
    Affiche les recettes publiques de l'utilisateur.
    """
    model = User
    template_name = 'accounts/user_profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_recipes'] = Recipe.objects.filter(
            author=self.object,
            is_published=True
        ).order_by('-created_at')
        return context
