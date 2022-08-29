from dataclasses import field
from rest_framework import serializers, permissions
from rest_framework.decorators import action, api_view, permission_classes
from django.core import exceptions as django_exceptions
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueTogetherValidator

from .models import Tags


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')

