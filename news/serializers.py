"""
Serializers for the News Application API.
This module converts complex model instances into JSON format for
REST API consumption and handles validation for incoming data.
"""

from rest_framework import serializers
from .models import Article, User, Newsletter


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Handles the conversion of user and publisher (editor) data for API
    responses.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model providing a flat representation.
    Includes read-only fields for author and publisher names to improve
    response readability.
    """

    author_name = serializers.ReadOnlyField(source="author.username")
    publisher_name = serializers.ReadOnlyField(source="publisher.username")

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_name",
            "publisher",
            "publisher_name",
            "approved",
            "created_at",
        ]
        read_only_fields = ["approved", "author"]


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for the Newsletter model.
    Uses primary key IDs for associated articles to prevent excessive
    nesting in the API output.
    """

    author_name = serializers.ReadOnlyField(source="author.username")
    # article_ids returns [1, 2, 3] instead of full article objects
    article_ids = serializers.PrimaryKeyRelatedField(
        source="articles", many=True, read_only=True
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "description",
            "author",
            "author_name",
            "article_ids",
            "created_at",
        ]
