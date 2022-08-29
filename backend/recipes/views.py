from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .serializers import TagSerializer
from .models import Tags


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer