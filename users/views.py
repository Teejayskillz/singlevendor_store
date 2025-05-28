from django.shortcuts import render

# Create your views here.
# ~/my_ecommerce_project/users/views.py

from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib.auth import login # Import login to automatically log in the user
from django.contrib import messages # For displaying messages

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically log in the user after registration
            messages.success(request, f'Account created for {user.username}! You are now logged in.')
            return redirect('products:product_list') # Redirect to product list after successful registration
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})