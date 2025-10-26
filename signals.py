from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile whenever a new User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    """Save the Profile whenever the User is saved (except during creation)."""
    # Only save profile if it's not a new user (profile is already created in create_profile)
    if not created and hasattr(instance, 'profile'):
        # Don't call save() to avoid infinite recursion
        # The profile will be saved directly from the form
        pass
