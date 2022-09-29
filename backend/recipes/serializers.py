import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from users.models import Follow, User
from users.serializers import UserSerializer

from .models import (FavoriteRecipe, Ingredient, IngredientsRecipe, Recipe,
                     ShoppingCartRecipe, Tag)


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели ингредиенты."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsRecipeListSerializer(serializers.ModelSerializer):
    """ Сериализатор для вспомогательной таблицы,
    передает список ингредиентов в рецепте.
    """
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientsRecipeCreateSerializer(serializers.ModelSerializer):
    """ Серилизатор для вспомогательной таблицы
    записи ингредиентов в рецепт."""
    amount = serializers.IntegerField(write_only=True)
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientsRecipe
        fields = ['id', 'amount']


class Base64ImageField(serializers.ImageField):
    """Для работы с изображением."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeListSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения списка рецептов."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientsRecipeListSerializer(
        many=True,
        source='ingredient_recipe'
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Определяет есть ли рецепт в избранном"""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Определяет есть ли рецепт в корзине."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCartRecipe.objects.filter(
            user=user,
            recipe=obj
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания, удаления и изменения рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientsRecipeCreateSerializer(many=True)
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        """ Создание рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_id = get_object_or_404(Ingredient, id=id)
            IngredientsRecipe.objects.create(
                recipe=recipe, ingredient=ingredient_id, amount=amount
            )
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """ Обновление рецепта."""
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get("image", instance.image)
        instance.tags.clear()
        tags_data = validated_data.pop('tags')
        for tag in tags_data:
            instance.tags.add(get_object_or_404(Tag, id=tag.id))
        instance.ingredients.clear()
        ingredients_data = validated_data.pop('ingredients')
        for ingredient in ingredients_data:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient_id)
            instance.ingredients.add(
                ingredient_obj,
                through_defaults={'amount': amount}
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context=self.context
        )
        return serializer.data


class ShortRecipeSerialazer(serializers.ModelSerializer):
    """ Сериализатор для моделей корзина и избранные рецепты."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с подпискасми."""
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        """Определяет подписан ли пользователь на автора."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            following=obj
        ).exists()

    def get_recipes(self, obj):
        """Получить рецепты автора в кратком виде."""
        recipes = Recipe.objects.filter(author=obj.id)
        serializers = ShortRecipeSerialazer(recipes, many=True)
        return (serializers.data)

    def get_recipes_count(self, obj):
        """Получить количество рецептов автора."""
        return Recipe.objects.filter(author=obj.id).count()
