from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    EmailValidator,
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models


class User(AbstractUser):
    """ Модель пользователь."""
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-_]+$',
                message='Недопустимое имя',
            )
        ],
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        validators=[EmailValidator],
    )
    first_name = models.TextField('Имя', max_length=150, blank=False)
    last_name = models.TextField('Фамилия', max_length=150, blank=False)
    password = models.CharField('Пароль', max_length=150, blank=False)
    is_subscribed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_username_email',
            ),
        ]


class Ingredients(models.Model):
    """ Модель ингредиенты. """
    name = models.CharField(
        'Наименование',
        max_length=150
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=16
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:20]

