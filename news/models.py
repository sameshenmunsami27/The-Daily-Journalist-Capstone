"""
Models for the News Application.
This module defines the data schema for Users (with role-based permissions),
Articles, Comments, and Newsletters.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending AbstractUser to include role-based
    access control and subscription management.
    """

    class Role(models.TextChoices):
        READER = "READER", "Reader"
        JOURNALIST = "JOURNALIST", "Journalist"
        EDITOR = "EDITOR", "Editor"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.READER
    )

    #  READER SUBSCRIPTIONS
    subscribed_publishers = models.ManyToManyField(
        "self", symmetrical=False, related_name="subscribed_readers",
        blank=True
    )

    subscribed_journalists = models.ManyToManyField(
        "self", symmetrical=False, related_name="journalist_followers",
        blank=True
    )

    def save(self, *args, **kwargs):
        """
        Override save to automatically manage staff status based on role
        and enforce role-specific field constraints.
        """
        # 1. Staff Status Logic
        if self.role in [self.Role.JOURNALIST, self.Role.EDITOR]:
            self.is_staff = True
        else:
            self.is_staff = False

        # 2. Save the instance first
        # Explicitly calling super with the class name can resolve
        # init/save conflicts
        super(User, self).save(*args, **kwargs)

        # 3. Role-Based Field Enforcement
        if self.role in [self.Role.JOURNALIST, self.Role.EDITOR]:
            # If they are a Journalist or Editor, they cannot have Reader
            # subscriptions
            if self.pk:
                self.subscribed_publishers.clear()
                self.subscribed_journalists.clear()

    def __str__(self):
        """Return a string representation of the user."""
        return f"{self.username} ({self.role})"


class Article(models.Model):
    """
    Represents a news article created by a Journalist.
    Requires approval by an Editor before becoming publicly visible.

    Attributes:
        approved (bool): Status indicating if the article is live.
        publisher (User): The editor who oversaw the publication.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    # Journalist Relation (Published independently)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="articles"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    publisher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_articles",
    )

    class Meta:
        # Default ordering for MySQL efficiency
        ordering = ['-created_at']

    def __str__(self):
        """Return the title of the article."""
        return self.title


class Comment(models.Model):
    """
    Represents a user-submitted comment on a specific article.
    """

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a summary of the comment and its author."""
        return f"Comment by {self.author.username} on {self.article.title}"


class Newsletter(models.Model):
    """
    Represents a collection of articles grouped together as a newsletter.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Journalist Relation (Published independently)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="newsletters"
    )

    articles = models.ManyToManyField(
        Article, related_name="newsletters", blank=True
    )

    def __str__(self):
        """Return the title of the newsletter."""
        return self.title
