# Generated by Django 3.2.15 on 2022-08-30 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_rename_ingredient_recipe_ingredients'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]