from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, ImageViewSet

app_name = 'recipe'

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('images', ImageViewSet)
router.register('recipe', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls))
]
