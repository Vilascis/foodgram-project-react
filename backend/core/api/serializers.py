import base64

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from core.abstract.serializers import AbstractSerializer
from core.cookbook.models import (
    FavoritesRecipes,
    Ingredient,
    IngredientForRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from core.users.models import Subscribe, User


class RegisterSerializer(AbstractSerializer):
    """Сериалайзер для регистрации пользователя."""

    password = serializers.CharField(
        max_length=128, min_length=8, write_only=True, required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        required=True,
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        ]
        lookup_field = 'username'

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(AbstractSerializer):
    """Список пользователей."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class SetPasswordSerializer(RegisterSerializer):

    current_password = serializers.CharField(
        max_length=128, min_length=8, write_only=True, required=True
    )
    new_password = serializers.CharField(
        max_length=128, min_length=8, write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ('current_password', 'new_password')

    def create(self, validated_data):
        return User.objects.change_password(**validated_data)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для описания ингредиентов в рецепте."""

    name = serializers.CharField(source='ingredient.name', read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAddSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipeShortInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsForRecipeSerializer(
        read_only=True, many=True, source='ingredients_amounts'
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and FavoritesRecipes.objects.filter(
                subscriber=self.context['request'].user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context['request'].user, recipe=obj
            ).exists()
        )


class FollowSerializer(UserSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    # def validate_author(self, obj):
    #     author = obj['following']
    #     user = obj['follower']
    #     if user == author:
    #         raise serializers.ValidationError('You can`t follow for yourself!')
    #     if (Subscribe.objects.filter(author=author, user=user).exists()):
    #         raise serializers.ValidationError('You have already subscribed!')
    #     return obj

    def get_recipes(self, obj):

        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipes = (
            obj.recipes.all()[:int(recipes_limit)]
            if recipes_limit else obj.recipes
        )
        serializer = serializers.ListSerializer(child=RecipeShortInfoSerializer())
        return serializer.to_representation(recipes)

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientAddSerializer(many=True)

    def validate_author(self, value):
        if self.context['request'].user != value:
            raise ValidationError(
                'Вы не можете создать рецепт для другого пользователя'
            )
        return value

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        extra_kwargs = {
            'image': {'required': True, 'allow_blank': False},
        }

    def get_ingredients(self, recipe, ingredients):
        IngredientForRecipe.objects.bulk_create(
            IngredientForRecipe(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientForRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeReadSerializer(instance, context=context).data

    def validate(self, obj):
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Для создания рецепта необходим минимум 1 ингредиент.'
            )

        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Для создания рецепта необходим минимум 1 тэг.'
            )

        if len(set(item.id for item in obj.get('tags'))) != len(obj.get('tags')):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        list_ingredient_id = [item['ingredient'].id for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(list_ingredient_id)
        if len(list_ingredient_id) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return obj


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления рецепта в избранное."""

    class Meta:
        model = FavoritesRecipes
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeShortInfoSerializer(instance.recipe, context=context).data
