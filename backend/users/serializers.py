from dataclasses import field
from .models import User
from rest_framework import serializers, permissions
from rest_framework.decorators import action, api_view, permission_classes
from django.core import exceptions as django_exceptions
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'password', 'is_subscribed',]


    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
