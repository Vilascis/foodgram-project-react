from django.conf import settings
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField('Название', max_length=254, unique=True)
    color = models.CharField('Цветовой код', max_length=7)
    slug = models.SlugField('slug', max_length=20, unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField('Название', max_length=150)
    measurement_unit = models.CharField('Единицы измерения', max_length=20)

    class Meta:
        ordering = ('id',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Назввание', max_length=200, blank=False, validators=[MaxLengthValidator(200)]
    )
    image = models.ImageField('Изображение', upload_to='recipes/')
    text = models.TextField(
        'Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientForRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name='ingredients',
        verbose_name='ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        verbose_name='тэги',
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class IngredientForRecipe(models.Model):
    """Ингредиенты, используемые для рецептов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients_amounts',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента', validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Количество ингредиента для рецепта'
        verbose_name_plural = 'Количество ингредиентов для рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='uq_recipe_ingredient',
            )
        ]


class FavoritesRecipes(models.Model):
    """Избранные рецепты."""

    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_subscriber',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранные рецепты',
    )
    favorite_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'recipe'], name='uq_favorite_subscriber_recipe'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.subscriber}'


class ShoppingCart(models.Model):
    """Рецепты в корзине."""

    recipe = models.ForeignKey(
        Recipe,
        related_name='cart',
        verbose_name='Рецепты в корзине',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='our_cart',
        verbose_name='Список список ингредиенов для покупок',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Корзина покупателя'
        verbose_name_plural = 'Корзины покупателей'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uq_recipe_users',
            ),
        )

    def __str__(self):
        return f'{self.user.username} добаил {self.recipe.name} в корзину.'
