"""
API Views for the News Application.
This module defines the RESTful API endpoints using Django Rest Framework,
including custom permissions and specialized actions for article approval
and subscription-based feeds.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Article, Newsletter
from .serializers import (
    ArticleSerializer,
    NewsletterSerializer,
)

# CUSTOM PERMISSIONS


class IsJournalist(permissions.BasePermission):
    """Allows access only to users with the Journalist role."""

    def has_permission(self, request, view):
        """Check if the requesting user has journalist privileges."""
        return (
            request.user.is_authenticated and
            request.user.role == "JOURNALIST"
        )


class IsEditor(permissions.BasePermission):
    """Allows access only to Editors or Superusers."""

    def has_permission(self, request, view):
        """Check if the requesting user has editor or admin privileges."""
        return request.user.is_authenticated and (
            request.user.role == "EDITOR" or request.user.is_superuser
        )


class IsAuthorOrEditor(permissions.BasePermission):
    """Allow authors of an object or editors to edit/delete it."""

    def has_object_permission(self, request, view, obj):
        """Determine if the user is the owner of the object or an editor."""
        if request.user.role == "EDITOR" or request.user.is_superuser:
            return True
        return obj.author == request.user


# VIEWSETS


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Article logic including creation,
    retrieval, and administrative approval.
    """

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return only approved articles for list/retrieve."""
        if self.action in ["list", "retrieve"]:
            return (
                Article.objects.filter(approved=True)
                .order_by("-created_at")
            )
        return super().get_queryset()

    def get_permissions(self):
        """Role-based access control for different API actions."""
        # Only Journalists can create articles
        if self.action == "create":
            permission_classes = [IsJournalist]
        # Journalists (owners) and Editors can update or delete
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthorOrEditor]
        # Only Editors can approve
        elif self.action == "approve":
            permission_classes = [IsEditor]
        elif self.action == "subscribed":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Assign the current user as the author upon article creation."""
        serializer.save(author=self.request.user, approved=False)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Approve article and send emails to followers."""
        article = self.get_object()
        article.approved = True
        article.save()

        # Build recipient list for the notification
        recipients = [settings.EMAIL_HOST_USER]

        if article.publisher:
            pub_readers = article.publisher.subscribed_readers.all()
            recipients.extend([r.email for r in pub_readers if r.email])

        journ_followers = article.author.journalist_followers.all()
        recipients.extend([r.email for r in journ_followers if r.email])

        article_url = f"http://127.0.0.1:8000/article/{article.id}/"

        # This call must be triggered for the test to pass
        send_mail(
            subject=f"New Article Approved: {article.title}",
            message=f"Your article is live!\nView here: {article_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(set(recipients)),
            fail_silently=False,
        )

        return Response(
            {"status": f"Article '{article.title}' approved."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="subscribed")
    def subscribed(self, request):
        """Retrieve articles from journalists or publishers followed
        by the user."""
        user = request.user
        articles = Article.objects.filter(approved=True).filter(
            author__journalist_followers=user
        ) | Article.objects.filter(approved=True).filter(
            publisher__subscribed_readers=user
        )

        serializer = self.get_serializer(
            articles.distinct().order_by("-created_at"), many=True
        )
        return Response(serializer.data)


class NewsletterViewSet(viewsets.ModelViewSet):
    """API endpoint to view, create, update, and delete newsletters."""

    queryset = Newsletter.objects.all().order_by("-created_at")
    serializer_class = NewsletterSerializer

    def get_permissions(self):
        """Allow Journalists/Editors to manage content; others just view."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAuthorOrEditor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
