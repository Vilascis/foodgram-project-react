from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from core.cookbook.models import (
    FavoritesRecipes,
    Ingredient,
    IngredientForRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from core.users.models import Subscribe, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
    )
    save_on_top = True
    save_as = True
    list_editable = ('email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    readonly_fields = ('id', 'public_id', 'get_recipes')
    empty_value_display = '-пусто-'
    fieldsets = (
        (
            'Информация о пользователе',
            {'fields': (('email', 'username', 'first_name', 'last_name'),)},
        ),
        ('Рецепты', {'fields': (('get_recipes',),)}),
        (
            'Идентификация пользователя',
            {
                'fields': (
                    (
                        'id',
                        'public_id',
                    ),
                )
            },
        ),
        (
            'Роли пользователя',
            {'fields': (('is_staff', 'is_active', 'role', 'is_superuser'),)},
        ),
        (
            'Данные об активности пользователя в приложении',
            {
                'fields': (
                    (
                        'last_login',
                        'date_joined',
                    ),
                )
            },
        ),
    )

    def get_recipes(self, obj):
        return ', '.join([recipe.name for recipe in obj.recipes.all()])

    get_recipes.short_description = 'Рецепты'


@admin.register(Subscribe)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'user')
    list_display_links = ('author',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_editable = ('color',)
    search_fields = ('name', 'slug')
    list_display_links = ('name',)

    fieldsets = ((None, {'fields': (('name', 'color', 'slug'),)}),)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'display_tag',
        'author',
        'get_image',
        'count_recipes_favorite',
    )
    readonly_fields = (
        'get_image',
        'count_recipes_favorite',
        'display_tag',
        'get_ingredients',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')

    fieldsets = (
        (
            'Кратко о рецепте:',
            {'fields': (('name', 'author', 'cooking_time', 'display_tag'),)},
        ),
        (
            'Ингредиенты:',
            {'fields': (('get_ingredients',),)},
        ),
        (
            'Описание',
            {
                'fields': (
                    (
                        'text',
                        'tags',
                    ),
                )
            },
        ),
        ('Изображение рецепта', {'fields': (('image', 'get_image'),)}),
    )

    def get_image(self, obj):
        return mark_safe(
            f'<img src={settings.MEDIA_URL}{obj.image} width="100" height="100"'
        )

    get_image.short_description = 'Изображение рецепта'

    def count_recipes_favorite(self, obj):
        return obj.favorite_recipe.count()

    count_recipes_favorite.short_description = 'Популярность рецепта'

    def display_tag(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    display_tag.short_description = 'Теги'

    def get_ingredients(self, obj):
        return ', '.join([ingredient.name for ingredient in obj.ingredients.all()])

    get_ingredients.short_description = 'Ингредиенты'


@admin.register(IngredientForRecipe)
class IngredientForRecipeAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')


@admin.register(FavoritesRecipes)
class FavoritesRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'get_favorite')
    readonly_fields = ('get_favorite',)

    def get_favorite(self, obj):
        return obj.subscriber

    get_favorite.short_description = 'Кто сохранил в избранном'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'get_shopping_cart')
    readonly_fields = ('get_shopping_cart',)

    def get_shopping_cart(self, obj):
        return obj.user

    get_shopping_cart.short_description = 'Кто добавил в коризину'


admin.site.site_title = 'Проект "Фудграм"'
admin.site.site_header = 'Проект "Фудграм"'
