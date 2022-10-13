from django.db.models import Sum
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import RecipeFilter, IngredientSearchFilter
from recipes.models import (
    FavoriteRecipe, Ingredient, IngredientsRecipe,
    Recipe, ShoppingCartRecipe, Tag
    )
from recipes.permissions import (
    IsAdminOrReadOnly,
    IsOwnerOrReadOnly
    )
from users.models import Follow, User
from .serializers import (
    IngredientSerializer,
    RecipeSerializer, ShortRecipeSerialazer,
    SubscribeSerializer, TagSerializer, UserSerializer
    )
from .utils import add_or_del_author, add_or_del_obj
from .pagination import LimitPageNumberPagination


class UserViewSet(UserViewSet):
    """ Вьюсет модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['GET'],
        detail=False,
         )
    @permission_classes([permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Показывает подписчиков."""
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        )
    @permission_classes([permissions.IsAuthenticated])
    def subscribe(self, request, id):
        """Подписаться или отписаться от автора."""
        return add_or_del_author(
            self,
            id=id,
            request=request,
            model=Follow,
            serializer=SubscribeSerializer
        )


class TagViewSet(ReadOnlyModelViewSet):
    """ Вьюсет модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """ Возвращает список всех ингредиентов из БД."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """ Вьюсет модели Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = (RecipeFilter)
    pagination_class = LimitPageNumberPagination
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated,),
        )
    def favorite(self, request, pk=None):
        """ Добавление/удаления рецепта в/из избранное."""
        return add_or_del_obj(
            self,
            pk=pk,
            request=request,
            model=FavoriteRecipe,
            serializer=ShortRecipeSerialazer
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated,),
        url_name='shopping_cart',
        url_path='shopping_cart'
        )
    def shopping_cart(self, request, pk=None):
        """ Добавление/удаления рецепта в/из корзины."""
        return add_or_del_obj(
            self,
            pk=pk,
            request=request,
            model=ShoppingCartRecipe,
            serializer=ShortRecipeSerialazer
        )

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
        )
    def download_shopping_cart(self, request):
        """ Получение списка покупок."""
        user = request.user
        file_name = 'shopping_list.txt'
        ingredients = IngredientsRecipe.objects.filter(
            recipe__cart_recipes__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('amount')).order_by('ingredient__name')
        response = HttpResponse(
            content_type='text/plain',
            charset='utf-8',
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        if ingredients.exists():
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
