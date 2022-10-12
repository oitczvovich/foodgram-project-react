from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """ Модель тег."""
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингредиент."""
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient')
        ]

    def __str__(self):
        return f'{self.name.title()} - ({self.measurement_unit})'


class Recipe(models.Model):
    """ Модель рецепт."""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка рецепта'
        )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
    )
    text = models.TextField('Описание')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsRecipe',
        verbose_name='Ингридиенты',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            'Минимальное время приготовления 1 минута'
        )],
        verbose_name='Время приготовления',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} - {self.author}'


class IngredientsRecipe(models.Model):
    """ Вспомогательная модель ингредиенты в рецепте."""
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            'Минимальное значение 1'
        )],
        verbose_name='Количество ',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингридиент',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name="unique_ingredient_recipe"
            )
        ]

    def __str__(self):
        return f' {self.ingredient}'


class FavoriteRecipe(models.Model):
    """ Модель избранные рецепты."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Рецепты'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name="unique_favorit_recipe"
            )
        ]


class ShoppingCartRecipe(models.Model):
    """ Модель корзина для покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipes',
        verbose_name='Корзина'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name="unique_cart_recipe"
            )
        ]
