from django.db import models


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
