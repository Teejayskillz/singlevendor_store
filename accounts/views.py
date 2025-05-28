
from django.shortcuts import render, get_object_or_404 , redirect
from django.contrib.auth.decorators import login_required
from .models import Profile # Import your Profile model
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm # Import the new forms
# from django.contrib.auth.models import User # Already imported by ProfileUpdateForm indirectly

@login_required # Ensures only logged-in users can access this page
def profile_detail(request):
    # The 'profile' attribute is automatically added to the User instance due to OneToOneField
    # If a profile doesn't exist for some reason (e.g., manually created user), get_object_or_404 will handle it.
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'accounts/profile_detail.html', {'profile': profile})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        # Pass instance=request.user to pre-fill the User form
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # Pass instance=request.user.profile to pre-fill the Profile form
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile_edit') # Redirect back to the same page after successful update
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile_edit.html', context)
