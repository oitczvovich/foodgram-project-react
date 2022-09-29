from django.contrib import admin
from recipes.models import (FavoriteRecipe, Ingredient, IngredientsRecipe,
                            Recipe, ShoppingCartRecipe, Tag)
from users.models import Follow, User

models = [
    Tag, IngredientsRecipe,
    FavoriteRecipe, ShoppingCartRecipe,
    ]

admin.site.register(models)


class IngredientRecipeInline(admin.TabularInline):
    """Представляет модель IngredientRecipe в интерфейсе администратора."""
    model = IngredientsRecipe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Представляет модель User в интерфейсе администратора."""
    list_display = ('id', 'username', 'email', 'first_name', 'last_name',)
    search_fields = ('username', 'email',)
    list_filter = ('email', 'first_name',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Представляет модель Follow в интерфейсе администратора."""
    list_display = ('user', 'following',)
    search_fields = ('following', 'user',)
    list_filter = ('following',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Представляет модель Recipe в интерфейсе администратора."""
    list_display = ('id', 'name', 'author', 'is_favorited')
    search_fields = ('author', 'name', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'

    def is_favorited(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    is_favorited.short_description = 'Кол-во в избранном'


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    """Представляет модель Ingredient в интерфейсе администратора."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
