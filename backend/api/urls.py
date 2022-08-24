from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, CatList

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
