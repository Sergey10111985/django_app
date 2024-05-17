from django import forms
from django.contrib.auth.models import User

from myauth.models import Profile


class AboutMeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = 'avatar',

