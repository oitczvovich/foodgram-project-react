import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """ Фильтр для рецептов по избранному,
        автору, списку покупок и тегам.
    """
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__name')
    is_favorited = django_filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                favorite_recipe__user=self.request.user
            )
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                cart_recipe__user=self.request.user
            )
        return Recipe.objects.all()
