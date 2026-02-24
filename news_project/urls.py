from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from news import views

urlpatterns = [
    # CUSTOM PASSWORD RESET OVERRIDES
    # Added 'accounts/' prefix to match the default auth paths exactly
    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="password_reset.html",
            email_template_name="password_reset_email.html",
            subject_template_name="password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Admin Panel
    path("admin/", admin.site.urls),
    # Built-in Login (Explicitly pointing to login.html in the root
    # templates folder)
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    # Built-in Auth (Handles remaining auth features)
    path("accounts/", include("django.contrib.auth.urls")),
    # Homepage
    path("", views.index, name="index"),
    # Registration & Authentication
    path("register/", views.register, name="register"),
    path("logout/", views.logout_user, name="logout"),
    # Articles
    path("article/<int:article_id>/", views.article_detail, name="article_detail"),
    path(
        "my-articles/", views.journalist_dashboard, name="journalist_dashboard"
    ),  # Added for Journalist management
    path("article/create/", views.create_article, name="create_article"),
    path("article/edit/<int:article_id>/", views.edit_article, name="edit_article"),
    path(
        "article/delete/<int:article_id>/", views.delete_article, name="delete_article"
    ),
    # Editor Dashboard
    path("dashboard/", views.editor_dashboard, name="editor_dashboard"),
    path("approve/<int:article_id>/", views.approve_article, name="approve_article"),
    # Newsletters
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path(
        "newsletter/<int:newsletter_id>/",
        views.newsletter_detail,
        name="newsletter_detail",
    ),
    path("newsletter/edit/", views.edit_newsletter, name="create_newsletter"),
    path(
        "newsletter/edit/<int:newsletter_id>/",
        views.edit_newsletter,
        name="edit_newsletter",
    ),
    path(
        "newsletter/delete/<int:newsletter_id>/",
        views.delete_newsletter,
        name="delete_newsletter",
    ),
    # Subscriptions & Comments
    path(
        "subscribe/<int:user_id>/<str:follow_type>/",
        views.toggle_subscribe,
        name="toggle_subscribe",
    ),
    path("my-subscriptions/", views.my_subscriptions, name="my_subscriptions"),
    path("comment/<int:article_id>/", views.add_comment, name="add_comment"),
]
