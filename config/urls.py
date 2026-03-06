"""
URL configuration for culinary_recipes project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from recipes.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('comptes/', include('accounts.urls', namespace='accounts')),
    path('recettes/', include('recipes.urls', namespace='recipes')),
    path('favoris/', include('favorites.urls', namespace='favorites')),
]

# Configuration pour les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
