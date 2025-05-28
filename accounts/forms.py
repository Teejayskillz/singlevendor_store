# accounts/forms.py
from django import forms
from django.contrib.auth.models import User # Django's built-in User model
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField() # Ensure email is handled as an EmailField

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # Fields from the User model

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'zip_code', 'country','profile_picture',] # Fields from your Profile model
        # If you uncommented profile_picture in models.py, add it here too:
        # fields = ['phone_number', 'address', 'city', 'zip_code', 'country', 'profile_picture']