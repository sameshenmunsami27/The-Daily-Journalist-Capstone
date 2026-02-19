"""
Signals for the News Application.
This module handles automated tasks triggered by database events, specifically
managing user permissions by synchronizing custom roles with Django Auth
Groups.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Signal receiver that automatically assigns a User to a Django Group
    based on their assigned 'role' (READER, JOURNALIST, or EDITOR).

    This ensures that built-in Django permission management stays in sync
    with the custom role field.
    """
    # Get the role based group
    group, _ = Group.objects.get_or_create(name=instance.role)

    # We use .add() directly. Django's ManyToManyField does
    # not add a duplicate if the user is already there.
    if not instance.groups.filter(id=group.id).exists():
        instance.groups.add(group)
