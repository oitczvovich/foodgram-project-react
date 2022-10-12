from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from users.models import User


def add_or_del_author(self, **kwargs):
    """Добавить или удалить автора."""
    request = kwargs['request']
    model = kwargs['model']
    serializer_type = kwargs['serializer']
    user = self.request.user
    following = get_object_or_404(User, id=kwargs['id'])
    subscribe = model.objects.filter(user=user, following=following)
    if request.method == 'DELETE':
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        if following == user:
            data = {'errors': 'Нельзя подписываться на самого себя'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        elif subscribe.exists():
            data = {'errors': 'Вы подписаны на данного автора.'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            model.objects.create(user=user, following=following)
            serializer = serializer_type(
                following,
                context={'request': request},
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )


def add_or_del_obj(self, **kwargs):
    """Добавить или удалить рецепт в переданной таблице."""
    recipe = self.get_object()
    model = kwargs['model']
    request = kwargs['request']
    serializer_type = kwargs['serializer']
    obj_in_table = model.objects.filter(
        user=self.request.user,
        recipe=recipe
    )
    if request.method == 'GET':
        if not obj_in_table.exists():
            model.objects.create(
                user=self.request.user,
                recipe=recipe
            )
            serilizer = serializer_type(
                recipe,
                context={'request': request}
            )
            return Response(serilizer.data)
        else:
            data = {'errors': 'Такой рецепт есть в списке.'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
    else:
        if obj_in_table.exists():
            obj_in_table.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            data = {'errors': 'Такого рецепта нет в списке.'}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
