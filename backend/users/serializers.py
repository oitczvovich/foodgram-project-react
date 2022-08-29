from email.policy import default
from rest_framework import serializers, permissions
from rest_framework.decorators import action, api_view, permission_classes
from django.core import exceptions as django_exceptions
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueTogetherValidator

from .models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"write_only": "password"},
        write_only=True
    )
    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        ]

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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            following=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate_following(self, value):
        user = self.context.get('request').user
        author = get_object_or_404(User, username=value)
        if author == user:
            raise serializers.ValidationError('На себя подписаться нельзя')
        return value
