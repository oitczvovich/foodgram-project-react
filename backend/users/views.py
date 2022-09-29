from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.serializers import SubscribeSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from .models import Follow, User
from .serializers import UserSerializer


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['GET'], detail=False)
    @permission_classes([permissions.IsAuthenticated])
    def subscriptions(self, request):
        """Показывает подписчиков."""
        user = request.user.id
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
        detail=True
        )
    @permission_classes([permissions.IsAuthenticated])
    def subscribe(self, requset, id):
        """Подписаться или отписаться от автора."""
        user = self.request.user
        following = get_object_or_404(User, id=id)
        subscribe = Follow.objects.filter(user=user, following=following)
        if requset.method == 'DELETE':
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
                Follow.objects.create(user=user, following=following)
                serializer = SubscribeSerializer(
                    following,
                    context={'request': requset},
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
