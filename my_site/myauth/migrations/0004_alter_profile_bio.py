# Generated by Django 5.0.1 on 2024-05-13 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0003_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
