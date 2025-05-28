# ~/my_ecommerce_project/accounts/urls.py

from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views # Import Django's built-in auth views for login/logout


app_name = 'accounts' # Define app_name for URL namespacing

urlpatterns = [
    path('profile/', views.profile_detail, name='profile_detail'),
    # Add more paths here later for editing, etc.
    path('profile/edit/', views.profile_edit, name='profile_edit'), 
   
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Ensure your logout URL is correctly set if it's not already
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/log_out.html'), name='logout'),
    # You might not need template_name='accounts/logged_out.html' if LOGOUT_REDIRECT_URL is set as we discussed
    # or you could just use: path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/',
         auth_views.PasswordChangeView.as_view(template_name='accounts/password_change_form.html'),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
         name='password_change_done'),
           # Password Reset URLs (Forgot Password)
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/password_reset_email.html', # Path to the email content
             subject_template_name='accounts/password_reset_subject.txt', # Path to the email subject
             success_url=reverse_lazy('accounts:password_reset_done') # Redirect after email is sent
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', # The unique link with user ID and token
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:password_reset_complete') # Redirect after password is reset
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]