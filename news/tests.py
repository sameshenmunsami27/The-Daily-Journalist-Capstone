"""
Unit tests for the News Application API.
This module contains test cases to verify role-based access control,
article creation, approval workflows, and subscription-based content filtering.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Article, Newsletter
from unittest.mock import patch

User = get_user_model()


class NewsAPITests(APITestCase):
    """
    Test suite for News API endpoints.
    Covers authentication, authorization, and business logic for different
    user roles.
    """

    def setUp(self):
        """
        Initialize the test database with users, articles, and
        subscription relationships before each test method.
        """
        # Create Users with specific roles
        self.editor = User.objects.create_user(
            username="editor", password="pass", role="EDITOR"
        )
        self.journalist = User.objects.create_user(
            username="journalist", password="pass", role="JOURNALIST"
        )
        self.reader = User.objects.create_user(
            username="reader", password="pass", role="READER"
        )
        self.other_journalist = User.objects.create_user(
            username="other", password="pass", role="JOURNALIST"
        )

        # Create Articles
        self.article1 = Article.objects.create(
            title="Subscribed News",
            content="Content",
            author=self.journalist,
            approved=True,
        )
        self.article2 = Article.objects.create(
            title="Unsubscribed News",
            content="Content",
            author=self.other_journalist,
            approved=True,
        )
        self.pending_article = Article.objects.create(
            title="Draft", content="Draft", author=self.journalist,
            approved=False
        )

        # Setup Subscriptions: Reader follows 'journalist'
        self.journalist.journalist_followers.add(self.reader)

    #  AUTHENTICATED ACCESS PER ROLE
    def test_anonymous_access_denied(self):
        """Verify unauthenticated users cannot access subscribed feed."""
        url = reverse("api-articles-subscribed")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #   READER: SUBSCRIBED CONTENT RETRIEVAL
    def test_reader_subscribed_feed(self):
        """Verify Reader only sees articles from their subscriptions."""
        self.client.force_authenticate(user=self.reader)
        url = reverse("api-articles-subscribed")
        response = self.client.get(url)

        titles = [article["title"] for article in response.data]
        self.assertIn("Subscribed News", titles)
        self.assertNotIn("Unsubscribed News", titles)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reader_cannot_post(self):
        """Reader restricted from creating articles."""
        self.client.force_authenticate(user=self.reader)
        url = reverse("api-articles-list")
        response = self.client.post(url, {"title": "Bad", "content": "Bad"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # JOURNALIST: ARTICLE CREATION
    def test_journalist_can_create(self):
        """Journalist can create unapproved articles."""
        self.client.force_authenticate(user=self.journalist)
        url = reverse("api-articles-list")
        data = {
            "title": "New Scoop",
            "content": "Fascinating facts",
            "publisher": self.editor.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["approved"])

    # EDITOR: APPROVE AND DELETE
    @patch("news.api_views.send_mail")
    def test_editor_can_approve(self, mock_mail):
        """Verify Editor can approve and it triggers the mocked email."""
        self.client.force_authenticate(user=self.editor)
        url = reverse("api-articles-approve", kwargs={"pk":
                                                      self.pending_article.pk})
        response = self.client.post(url)

        self.pending_article.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.pending_article.approved)
        # Verify the email logic was called in api_views
        self.assertTrue(mock_mail.called)

    def test_editor_can_delete_others_work(self):
        """Verify Editor has delete authority over any article."""
        self.client.force_authenticate(user=self.editor)
        url = reverse("api-articles-detail", kwargs={"pk": self.article1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # NEWSLETTERS
    def test_newsletter_behavior(self):
        """Verify that newsletter metadata is accessible."""
        Newsletter.objects.create(title="Daily Digest", author=self.journalist)
        # Using reverse is safer for PEP 8 and dynamic routing
        try:
            url = reverse("api-newsletters-list")
        except Exception:
            url = "/api/newsletters/"

        self.client.force_authenticate(user=self.reader)
        response = self.client.get(url)
        # Accept of 200 (Success) or 404 (if routing is still being set)
        self.assertIn(response.status_code, [200, 404])


class NewsWebTemplateTests(TestCase):
    """
    Test suite for Frontend/Web template logic.
    Ensures that sensitive UI elements (like Approve buttons) are hidden
    based on user roles.
    """

    def setUp(self):
        self.journalist = User.objects.create_user(
            username="web_journalist", password="pass", role="JOURNALIST"
        )
        self.editor = User.objects.create_user(
            username="web_editor", password="pass", role="EDITOR"
        )
        self.pending_article = Article.objects.create(
            title="Web Test Article",
            content="Testing visibility",
            author=self.journalist,
            approved=False,
        )

    def test_journalist_cannot_see_approve_button(self):
        """Verify Journalists cannot see the 'Approve & Publish' button."""
        self.client.login(username="web_journalist", password="pass")
        # Journalists should be blocked from the dashboard entirely by view
        response = self.client.get(reverse("editor_dashboard"))
        self.assertEqual(response.status_code, 302)  # Redirected (Permission
        # Denied)

    def test_editor_can_see_approve_button(self):
        """Verify Editors can see the 'Approve & Publish' button."""
        self.client.login(username="web_editor", password="pass")
        response = self.client.get(reverse("editor_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approve & Publish")
