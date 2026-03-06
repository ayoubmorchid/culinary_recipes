from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.register, name='register'),
    path('connexion/', views.user_login, name='login'),
    path('deconnexion/', views.user_logout, name='logout'),
    path('profil/', views.profile, name='profile'),
    path('profil/<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
]
