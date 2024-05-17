# Generated by Django 5.0.1 on 2024-05-09 03:56

import myauth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=myauth.models.avatar_directory_path),
        ),
    ]