from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    """ Модель тег."""
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Ссылка',
        max_length=200,
        unique=True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}, {self.color}, {self.slug}'


class Ingredient(models.Model):
    """ Модель ингредиент."""
    name = models.CharField(
        'Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name.title()} - ({self.measurement_unit})'


class Recipe(models.Model):
    """ Модель рецепт."""
    author = models.ForeignKey(
        User,
        related_name='recipe',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
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
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            'Укажите время приготовления в минутах'
        )],
        verbose_name='Время приготовления',
    )

    class Meta:
        ordering = ('-id',)
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
        verbose_name='Количество продукта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f' {self.ingredient}'


class FavoriteRecipe(models.Model):
    """ Модель избранные рецепты."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепты'
    )

    class Meta:
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
        related_name='cart_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe',
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
