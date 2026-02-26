"""
Frontend View Logic for the News Application.
This module handles all web-based interactions including article management,
newsletter curation, user subscriptions, and editor approval workflows.
"""

import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from .models import Article, User, Comment, Newsletter  # noqa
from django import forms

# --- ACCESS CONTROL HELPERS ---


def is_editor(user):
    """Check if the user is an Editor, Admin, or Superuser."""
    return user.is_authenticated and (
        user.role in ["EDITOR", "ADMIN"] or user.is_superuser
    )


def is_journalist(user):
    """Check if the user is a Journalist, Admin, or Superuser."""
    return user.is_authenticated and (
        user.role in ["JOURNALIST", "ADMIN"] or user.is_superuser
    )


def is_staff_member(user):
    """Check if the user belongs to any staff management roles."""
    return user.is_authenticated and (
        user.role in ["JOURNALIST", "EDITOR", "ADMIN"] or user.is_superuser
    )


# --- PUBLIC VIEWS ---


def index(request):
    """Renders the main landing page with approved articles."""
    articles = Article.objects.filter(approved=True).order_by("-created_at")
    form = RegistrationForm()
    context = {
        "articles": articles,
        "portal_name": "The Daily Journalist",
        "form": form,
    }
    return render(request, "index.html", context)


def article_detail(request, article_id):
    """Displays a single article. Restricts unapproved articles to authors
    /staff."""
    article = get_object_or_404(Article, id=article_id)

    if not article.approved:
        user_is_author = request.user == article.author
        user_is_privileged = is_editor(request.user)

        if not (user_is_author or user_is_privileged):
            raise Http404("This article has not been approved yet.")

    return render(request, "article_detail.html", {"article": article})


# --- EDITOR & ADMIN LOGIC ---


@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    """Dashboard for reviews. Admins and Editors can see this."""
    pending = Article.objects.filter(approved=False).order_by("-created_at")
    return render(request, "editor_dashboard.html", {"articles": pending})


@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    """Approves article and notifies followers."""
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        article.approved = True
        article.save()

        recipient_list = [settings.EMAIL_HOST_USER]
        if article.publisher:
            for r in article.publisher.subscribed_readers.all():
                if r.email:
                    recipient_list.append(r.email)

        for r in article.author.journalist_followers.all():
            if r.email:
                recipient_list.append(r.email)

        article_url = f"http://127.0.0.1:8000/article/{article.id}/"

        send_mail(
            subject=f"New Article Approved: {article.title}",
            message=f"Article '{article.title}' is live!\nView: {article_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(set(recipient_list)),
            fail_silently=False,
        )

        try:
            requests.post(
                "https://jsonplaceholder.typicode.com/posts",
                json={"title": article.title, "userId": article.author.id},
                timeout=5,
            )
            messages.success(request, f"Article '{article.title}' published!")
        except requests.RequestException:  # Catch specifically
            # network-related errors
            messages.error(request, "Social media notification failed.")

        return redirect("editor_dashboard")
    return redirect("index")


# --- SUBSCRIPTION LOGIC ---


@login_required
def toggle_subscribe(request, user_id, follow_type):
    """Handle subscriptions. Restricted to READER role only."""
    if request.user.role != "READER":
        messages.warning(
            request, "Staff and Admin accounts cannot maintain subscription"
            "lists."
        )
        return redirect(request.META.get("HTTP_REFERER", "index"))

    target_user = get_object_or_404(User, id=user_id)
    if follow_type == "journalist":
        if request.user in target_user.journalist_followers.all():
            target_user.journalist_followers.remove(request.user)
        else:
            target_user.journalist_followers.add(request.user)
    elif follow_type == "publisher":
        if request.user in target_user.subscribed_readers.all():
            target_user.subscribed_readers.remove(request.user)
        else:
            target_user.subscribed_readers.add(request.user)

    return redirect(request.META.get("HTTP_REFERER", "index"))


@login_required
def my_subscriptions(request):
    """Display subscriptions for Reader accounts."""
    if request.user.role != "READER":
        return redirect("index")
    journalists = User.objects.filter(journalist_followers=request.user)
    publishers = User.objects.filter(subscribed_readers=request.user)
    return render(
        request,
        "my_subscriptions.html",
        {"journalists": journalists, "publishers": publishers},
    )


# --- ARTICLE ACTIONS ---


@login_required
@user_passes_test(is_journalist)
def create_article(request):
    """Journalists and Admins can create articles."""
    if request.method == "POST":
        p_id = request.POST.get("publisher")

        # Safer and clearer way to fetch the publisher user
        pub_user = None
        if p_id and p_id != "independent":
            try:
                pub_user = User.objects.get(id=p_id)
            except User.DoesNotExist:
                pub_user = None

        Article.objects.create(
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            author=request.user,
            publisher=pub_user,
            approved=False,
        )
        messages.success(request, "Article submitted for review.")
        return redirect("index")
    return render(
        request, "create_article.html", {"editors": User.objects.
                                         filter(role="EDITOR")}
    )


@login_required
def edit_article(request, article_id):
    """Authors, Editors, and Admins can update articles."""
    article = get_object_or_404(Article, id=article_id)
    if request.user != article.author and not is_editor(request.user):
        return HttpResponseForbidden("Permission denied.")

    if request.method == "POST":
        article.title = request.POST.get("title")
        article.content = request.POST.get("content")
        pub_id = request.POST.get("publisher")
        article.publisher_id = None if pub_id == "independent" else pub_id
        article.approved = False
        article.save()
        messages.success(request, "Article updated!")
        return redirect("index")
    return render(
        request,
        "edit_article.html",
        {"article": article, "editors": User.objects.filter(role="EDITOR")},
    )


@login_required
@user_passes_test(is_staff_member)
def delete_article(request, article_id):
    """Authors, Editors, and Admins can delete articles."""
    article = get_object_or_404(Article, id=article_id)
    if request.user == article.author or is_editor(request.user):
        article.delete()
        messages.success(request, "Article deleted.")
    return redirect("index")


# --- NEWSLETTER LOGIC ---


def newsletter_list(request):
    return render(
        request,
        "newsletter_list.html",
        {"newsletters": Newsletter.objects.all().order_by("-created_at")},
    )


def newsletter_detail(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    return render(
        request,
        "newsletter_detail.html",
        {"newsletter": newsletter, "can_edit": is_staff_member(request.user)},
    )


@login_required
@user_passes_test(is_staff_member)
def edit_newsletter(request, newsletter_id=None):
    newsletter = (
        get_object_or_404(Newsletter, id=newsletter_id)
        if newsletter_id else None
    )
    if request.method == "POST":
        title, desc = request.POST.get("title"),
        request.POST.get("description")
        if not newsletter:
            newsletter = Newsletter.objects.create(
                title=title, description=desc, author=request.user
            )
        else:
            newsletter.title, newsletter.description = title, desc
            newsletter.save()
        newsletter.articles.set(request.POST.getlist("articles"))
        return redirect("newsletter_detail", newsletter_id=newsletter.id)
    return render(
        request,
        "edit_newsletter.html",
        {"newsletter": newsletter, "articles":
         Article.objects.filter(approved=True)},
    )


@login_required
@user_passes_test(is_staff_member)
def delete_newsletter(request, newsletter_id):
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    if request.user == newsletter.author or is_editor(request.user):
        newsletter.delete()
    return redirect("newsletter_list")


# --- COMMENTS & AUTHENTICATION ---


@login_required
def add_comment(request, article_id):
    """Allow authenticated users to post comments on approved articles."""
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        text = request.POST.get("comment_text")
        if text:
            Comment.objects.create(article=article, author=request.user,
                                   text=text)
            messages.success(request, "Comment posted!")
    return redirect("article_detail", article_id=article.id)


def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect("index")


class RegistrationForm(forms.ModelForm):
    """Public Registration Form: Strictly Reader, Journalist,
       and Editor only."""

    ROLE_CHOICES = [
        ("READER", "Reader"),
        ("JOURNALIST", "Journalist"),
        ("EDITOR", "Editor"),
    ]
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.role = form.cleaned_data["role"]
            user.save()
            login(request, user)
            return redirect("index")
    return render(request, "register.html", {"form": RegistrationForm()})


@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    articles = (
        Article.objects.filter(author=request.user)
        .order_by("-created_at")
    )
    return render(request, "journalist_dashboard.html", {"articles": articles})
