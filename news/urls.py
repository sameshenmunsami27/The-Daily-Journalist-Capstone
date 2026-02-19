"""
URL configuration for the news app.
Defines routes for article viewing, editor dashboards, and user subscriptions.
"""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .api_views import ArticleViewSet, NewsletterViewSet

# Create a router and register our ViewSets
router = DefaultRouter()
router.register(r"articles", ArticleViewSet, basename="api-articles")
router.register(r"newsletters", NewsletterViewSet, basename="api-newsletters")

urlpatterns = [
    #  Public Views
    path("", views.index, name="index"),
    path("article/<int:article_id>/", views.article_detail,
         name="article_detail"),
    #  Editor Logic
    path("editor/dashboard/", views.editor_dashboard, name="editor_dashboard"),
    path(
        "editor/approve/<int:article_id>/",
        views.approve_article,
        name="approve_article",
    ),
    #  Comment Logic
    path("article/<int:article_id>/comment/", views.add_comment,
         name="add_comment"),
    #  Subscription Logic
    path(
        "subscribe/<int:user_id>/<str:follow_type>/",
        views.toggle_subscribe,
        name="toggle_subscribe",
    ),
    path("my-subscriptions/", views.my_subscriptions, name="my_subscriptions"),
    #  Article Actions (Creation, Edit, Delete)
    path("article/create/", views.create_article, name="create_article"),
    path("article/edit/<int:article_id>/", views.edit_article,
         name="edit_article"),
    path(
        "article/delete/<int:article_id>/", views.delete_article,
        name="delete_article"
    ),
    #  Newsletter Logic
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path(
        "newsletter/<int:newsletter_id>/",
        views.newsletter_detail,
        name="newsletter_detail",
    ),
    path("newsletter/new/", views.edit_newsletter, name="create_newsletter"),
    path(
        "newsletter/edit/<int:newsletter_id>/",
        views.edit_newsletter,
        name="edit_newsletter",
    ),
    #  Newsletter Delete
    path(
        "newsletter/delete/<int:newsletter_id>/",
        views.delete_newsletter,
        name="delete_newsletter",
    ),
    #  Authentication Logic
    path("login/", LoginView.as_view(template_name="login.html"),
         name="login"),
    path("logout/", LogoutView.as_view(next_page="index"), name="logout"),
    # Password Reset Logic
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # --- REST API Endpoints ---
    path("api/", include(router.urls)),
    path("api/token/", obtain_auth_token, name="api_token_auth"),
]
