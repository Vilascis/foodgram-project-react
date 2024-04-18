from rest_framework import routers

from django.urls import include, path

from core.api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from core.users.views import UserViewSet

router = routers.SimpleRouter()


router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
