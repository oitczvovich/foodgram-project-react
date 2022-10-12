from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter
from .models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    """ Фильтр для рецептов по избранному,
        автору, списку покупок и тегам.
    """
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart_recipes__user=self.request.user)
        return queryset
