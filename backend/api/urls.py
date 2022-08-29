from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet
from recipes.views import TagViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
