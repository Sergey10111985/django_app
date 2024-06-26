from django.contrib.auth.models import User
from django.db import models


def avatar_directory_path(instance: "Profile", filename: str) -> str:
    return 'avatars/profile_{id}/{filename}'.format(
        id=instance.pk,
        filename=filename
    )


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    bio = models.TextField(max_length=500, blank=True, null=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to=avatar_directory_path, null=True)
