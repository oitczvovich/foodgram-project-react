from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    FavoriteRecipe, Ingredient, IngredientsRecipe,
    Recipe, ShoppingCartRecipe, Tag
    )
from users.models import Follow, User
from .fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели пользователь."""
    password = serializers.CharField(
        style={"write_only": "password"},
        write_only=True
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
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
            'is_subscribed',
        ]

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            following=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели подписки."""
    user = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate_following(self, value):
        user = self.context.get('request').user
        author = get_object_or_404(User, username=value)
        if author == user:
            raise serializers.ValidationError('На себя подписаться нельзя')
        return value


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


class RecipeListSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения списка рецептов."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientsRecipeListSerializer(
        many=True,
        source='ingredient_recipes'
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

    def check_ingredients(self, data):
        validated_items = []
        existed = []
        for item in data:
            ingredient = get_object_or_404(Ingredient, pk=item['id'])
            if ingredient in validated_items:
                existed.append(ingredient)
            validated_items.append(ingredient)
        if existed:
            errors = 'Ингредиент уже добавлен в рецепт'
            raise serializers.ValidationError(errors)

    def validate(self, data):
        ingredients = data.get('ingredients')
        self.check_ingredients(ingredients)
        data['ingredients'] = ingredients
        return data

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            recipe_ingredient = IngredientsRecipe(
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient['id']
                ),
                recipe=recipe,
                amount=amount
            )
            ingredient_list.append(recipe_ingredient)
        IngredientsRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        """ Создание рецепта."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.save()
        return recipe

    def update(self, recipe, validated_data):
        """ Обновление рецепта."""
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        IngredientsRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

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
    recipes = ShortRecipeSerialazer(read_only=True, many=True)
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

    def get_recipes_count(self, obj):
        """Получить количество рецептов автора."""
        return Recipe.objects.filter(author=obj.id).count()
