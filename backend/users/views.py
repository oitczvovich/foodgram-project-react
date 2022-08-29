from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes

from .models import Follow, User
from .serializers import UserSerializer
from djoser.views import UserViewSet


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['GET'], detail=False)
    @permission_classes([permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user.id
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = UserSerializer(
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
        user = self.request.user
        following = get_object_or_404(User, id=id)
        subscribe = Follow.objects.filter(user=user, following=following)
        if requset.method == 'DELETE':
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        elif requset.method == 'POST':
            if following == user:
                data = {'errors': 'Нельзя подписываться на самого себя'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            elif subscribe.exists():
                data = {'errors': 'Вы подписаны на данного автора.'}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                Follow.objects.create(user=user, following=following)
                serializer = UserSerializer(
                    following,
                    context={'request': requset},
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

