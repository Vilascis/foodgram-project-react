from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from core.api.filters import IngredientFilter, RecipeFilter
from core.api.pagination import CustomPaginator
from core.api.permissions import IsAuthorOrReadOnly
from core.api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeSerializer,
    RecipeShortInfoSerializer,
    TagSerializer,
)
from core.api.utils import download_pdf
from core.cookbook.models import (
    FavoritesRecipes,
    Ingredient,
    IngredientForRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ['get',]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, IngredientFilter)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        object = FavoritesRecipes.objects.filter(subscriber=user, recipe=recipe)

        if request.method == 'POST':
            if object.exists():
                return Response(
                    {'errors': 'Этот рецепт уже добавлен в Избранное'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            FavoritesRecipes.objects.create(subscriber=user, recipe=recipe)
            serializer = RecipeShortInfoSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True, methods=['post', 'delete'], permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление рецепта в корзину покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        object = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if object.exists():

                return Response({
                    'errors': 'Этот рецепт уже добавлен в Избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortInfoSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепта нет корзине покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """Загрузка файла с ингредиентами для покупки."""
        ingredients = (
            IngredientForRecipe.objects.filter(recipe__cart__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name', 'total_amount', 'ingredient__measurement_unit'
            )
        )
        return download_pdf(ingredients)
