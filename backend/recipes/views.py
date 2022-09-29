from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter
from .models import (FavoriteRecipe, Ingredient, IngredientsRecipe, Recipe,
                     ShoppingCartRecipe, Tag)
from .permissions import IsAdminOrAuthor
from .serializers import (IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShortRecipeSerialazer,
                          TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ Возвращает список всех ингредиентов из БД."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(ModelViewSet):
    """ Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrAuthor,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=(permissions.IsAuthenticated,),
        )
    def favorite(self, request, pk=None):
        """ Добавление/удаления рецепта в/из избранное."""
        recipe = self.get_object()
        obj_in_table = FavoriteRecipe.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if request.method == 'POST':
            if not obj_in_table:
                FavoriteRecipe.objects.create(
                    user=self.request.user,
                    recipe=recipe
                )
                serilizer = ShortRecipeSerialazer(
                    recipe,
                    context={'request': request}
                )
                return Response(serilizer.data)
            else:
                data = {'errors': 'Такой рецепт есть в избранных.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            if obj_in_table:
                obj_in_table.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                data = {'errors': 'Такого рецепта нет в избранных.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
        )
    def shopping_cart(self, request, pk=None):
        """ Добавление/удаления рецепта в/из корзины."""
        recipe = self.get_object()
        obj_in_table = ShoppingCartRecipe.objects.filter(
            user=self.request.user,
            recipe=recipe
        )
        if request.method == 'POST':
            if not obj_in_table:
                ShoppingCartRecipe.objects.create(
                    user=self.request.user,
                    recipe=recipe
                )
                serilizer = ShortRecipeSerialazer(
                    recipe,
                    context={'request': request}
                )
                return Response(serilizer.data)
            else:
                data = {'errors': 'Рецепт есть в корзине.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            if obj_in_table:
                obj_in_table.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                data = {'errors': 'Такого рецепта нет в корзине.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
        )
    def download_shopping_cart(self, request):
        """ Получение списка покупок."""
        user = request.user
        file_name = 'shopping_list.txt'
        ingredients = IngredientsRecipe.objects.filter(
            recipe__cart_recipe__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('amount')).order_by('ingredient__name')
        response = HttpResponse(
            content_type='text/plain',
            charset='utf-8',
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        if len(ingredients):
            response.write('Список продуктов к покупке:\n')
            for ingredient in ingredients:
                response.write(
                    f'\u2610 {ingredient["ingredient__name"].title()} '
                    f'({ingredient["ingredient__measurement_unit"]}) '
                    f'- {ingredient["ingredient_amount"]}\n'
                )
            response.write('\nПроект Foodgram от Gostinci\n')
            return response
        response.write('Ваш список покупок пуст\n')
        return response
