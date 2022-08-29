from django.contrib import admin
from users.models import User, Follow

user_models = [User, Follow]

admin.site.register(user_models)



