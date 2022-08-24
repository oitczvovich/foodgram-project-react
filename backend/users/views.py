from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination

from .models import User
from .serializers import UserSerializer
from djoser.views import UserViewSet


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = UserSerializer

class CatList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


