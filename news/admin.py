"""
Admin configuration for the News Application.
This module defines how models are displayed and managed within the
Django administration interface, including custom user role management
and article approval workflows.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Article, Comment, Newsletter


# Customizing the User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Customizes the User management interface.
    Extends the standard UserAdmin to include role-based fields and
    many-to-many subscription relationships.
    """

    # This adds the "Available" and "Chosen" boxes for Many-to-Many fields
    filter_horizontal = (
        "groups",
        "user_permissions",
        "subscribed_publishers",
        "subscribed_journalists",
    )

    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role", "is_staff")

    # Allows changing roles directly from the list view
    list_editable = ("role",)

    # This ensures your custom fields show up when editing a user
    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom Fields",
            {"fields": ("role", "subscribed_publishers",
                        "subscribed_journalists")},
        ),
    )


# Customizing the Article Admin
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin interface for managing news articles.
    Provides functionality for quick approval and filtering by publisher.
    """

    list_display = ("title", "author", "publisher", "approved", "created_at")
    list_filter = ("approved", "publisher", "created_at")
    search_fields = ("title", "content")
    list_editable = ("approved",)


# Customizing the Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for moderating comments.
    Allows administrators to track which comments belong to which articles.
    """

    list_display = ("author", "article", "created_at")
    list_filter = ("created_at", "article")
    search_fields = ("text",)


# Customizing the Newsletter Admin
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin interface for managing newsletters.
    Facilitates the grouping of multiple articles into a single newsletter
    using a horizontal filter interface.
    """

    list_display = ("title", "author", "created_at")
    list_filter = ("author", "created_at")
    # Enables the "Chosen" box for the many-to-many relationship with Article
    filter_horizontal = ("articles",)
