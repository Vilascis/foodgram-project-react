from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from core.cookbook.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.CharFilter(method='filter_author')

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_author(self, queryset, name, value):
        """Фильтрация по автору рецепта."""
        if value:
            return queryset.filter(author__public_id=value)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов для отображения в избранном."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite_recipe__subscriber=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов дл отображения в карзине покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    """Фильтр для ингредиентов."""

    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)
