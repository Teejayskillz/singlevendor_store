from django.db import models
from django.conf import settings # To get the AUTH_USER_MODEL
from django.db.models.signals import post_save # Used to catch user creation event
from django.dispatch import receiver # Decorator for signals

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Add any additional fields you want for the user's profile here
    # For example:
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True) # Uncomment if you configure media files

    def __str__(self):
        return f'Profile for {self.user.username}'

# --- Signal to automatically create a Profile when a new User is created ---
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()