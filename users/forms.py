# ~/my_ecommerce_project/users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User # Or your custom user model if you have one

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True) # Require email for registration

    class Meta(UserCreationForm.Meta):
        model = User # Use Django's default User model
        fields = UserCreationForm.Meta.fields + ('email',) # Add email to the fields

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email