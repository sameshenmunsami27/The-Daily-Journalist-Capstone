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
from .models import Article, User, Comment, Newsletter
from django import forms

# ACCESS CONTROL HELPERS


def is_editor(user):
    """Check if the user is an authenticated Editor or Superuser."""
    return user.is_authenticated and (user.role == "EDITOR" or
                                      user.is_superuser)


def is_journalist(user):
    """Check if the user is an authenticated Journalist or Superuser."""
    return user.is_authenticated and (user.role == "JOURNALIST" or
                                      user.is_superuser)


def is_staff_member(user):
    """Check if the user belongs to the Journalist or Editor staff roles."""
    return user.is_authenticated and (
        user.role in ["JOURNALIST", "EDITOR"] or user.is_superuser
    )


# PUBLIC VIEWS


def index(request):
    """
    Renders the main landing page of the news portal.

    Args:
        request: The HTTP request object.
    Returns:
        A rendered HTML page containing a list of approved articles and
    """
    articles = Article.objects.filter(approved=True).order_by("-created_at")

    # Form instance added here so it renders on the main page
    form = RegistrationForm()

    context = {
        "articles": articles,
        "portal_name": "The Daily Journalist",
        "form": form
    }
    return render(request, "index.html", context)


def article_detail(request, article_id):
    """
    Handles the retrieval and display of a single news article.

    Args:
        request: The HTTP request object.
        article_id (int): The primary key of the article to display.
    Raises:
        Http404: If the article is unapproved and the user is not the author
        or an editor.
    """
    # Fetch the article by ID only (removing the strict approved=
    # True filter)
    article = get_object_or_404(Article, id=article_id)

    # Permission Check: If article is not approved, only Author or Editor
    # can see it
    if not article.approved:
        user_is_author = request.user == article.author
        user_is_editor = is_editor(request.user)

        if not (user_is_author or user_is_editor):
            # If a regular Reader tries to access an unapproved link,
            # return 404
            raise Http404("This article has not been approved yet.")

    return render(request, "article_detail.html", {"article": article})


# EDITOR LOGIC


@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    """Display a dashboard for editors to review pending articles."""
    # Fixed: Combined onto one line to avoid indentation errors
    pending = Article.objects.filter(approved=False).order_by("-created_at")
    return render(request, "editor_dashboard.html", {"articles": pending})


@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    """
    Handles the retrieval and display of a single news article.

    Args:
        request: The HTTP request object.
        article_id (int): The primary key of the article to display.
    Raises:
        Http404: If the article is unapproved and the user is not the author
        or an editor.
    """
    article = get_object_or_404(Article, id=article_id)

    if request.method == "POST":
        article.approved = True
        article.save()

        recipient_list = [settings.EMAIL_HOST_USER]

        # Collect reader emails
        if article.publisher:
            for reader in article.publisher.subscribed_readers.all():
                if reader.email:
                    recipient_list.append(reader.email)

        for reader in article.author.journalist_followers.all():
            if reader.email:
                recipient_list.append(reader.email)

        article_url = f"http://127.0.0.1:8000/article/{article.id}/"

        send_mail(
            subject=f"New Article Approved: {article.title}",
            message=(
                f"Your article '{article.title}' is now live!\n"
                f"View it here: {article_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(set(recipient_list)),
            fail_silently=False,
        )

        placeholder_url = "https://jsonplaceholder.typicode.com/posts"
        payload = {
            "title": article.title,
            "body": "Published #NewsApp",
            "userId": article.author.id,
        }

        try:
            requests.post(placeholder_url, json=payload, timeout=5)
            messages.success(request, f"Article '{article.title}' published!")
        except requests.exceptions.RequestException:
            messages.error(request, "Social media notification failed.")

        return redirect("editor_dashboard")

    return redirect("index")


# SUBSCRIPTION LOGIC


@login_required
def toggle_subscribe(request, user_id, follow_type):
    """Handle subscribing and unsubscribing from journalists or publishers."""
    if request.user.role != "READER":
        messages.error(request, "Only Readers can subscribe.")
        return redirect(request.META.get("HTTP_REFERER", "index"))

    target_user = get_object_or_404(User, id=user_id)

    if follow_type == "journalist":
        if request.user in target_user.journalist_followers.all():
            target_user.journalist_followers.remove(request.user)
            messages.info(request, f"Unsubscribed from {target_user.username}")
        else:
            target_user.journalist_followers.add(request.user)
            messages.success(request, f"Subscribed to {target_user.username}!")

    elif follow_type == "publisher":
        if request.user in target_user.subscribed_readers.all():
            target_user.subscribed_readers.remove(request.user)
            messages.info(request, f"Unsubscribed from {target_user.username}")
        else:
            target_user.subscribed_readers.add(request.user)
            messages.success(request, f"Subscribed to {target_user.username}!")

    return redirect(request.META.get("HTTP_REFERER", "index"))


@login_required
def my_subscriptions(request):
    """Display a list of all journalists and publishers the user follows."""
    if request.user.role != "READER":
        return redirect("index")

    journalists = User.objects.filter(journalist_followers=request.user)
    publishers = User.objects.filter(subscribed_readers=request.user)

    return render(
        request,
        "my_subscriptions.html",
        {
            "journalists": journalists,
            "publishers": publishers,
        },
    )


#  ARTICLE ACTIONS


@login_required
@user_passes_test(is_journalist)
def create_article(request):
    """Allow journalists to create new articles for editor review."""
    if request.method == "POST":
        p_id = request.POST.get("publisher")

        # Handle 'Independent Journalist' option
        pub_user = None
        if p_id and p_id != "independent":
            pub_user = User.objects.get(id=p_id)

        Article.objects.create(
            title=request.POST.get("title"),
            content=request.POST.get("content"),
            author=request.user,
            publisher=pub_user,
            approved=False,
        )
        messages.success(request, "Article submitted for review.")
        return redirect("index")

    editors = User.objects.filter(role="EDITOR")
    return render(request, "create_article.html", {"editors": editors})


@login_required
def edit_article(request, article_id):
    """Allow authors or editors to update article content."""
    article = get_object_or_404(Article, id=article_id)

    if request.user != article.author and request.user.role != "EDITOR":
        return HttpResponseForbidden("Permission denied.")

    if request.method == "POST":
        article.title = request.POST.get("title")
        article.content = request.POST.get("content")
        pub_id = request.POST.get("publisher")

        # Handle 'Independent Journalist' update
        if pub_id == "independent":
            article.publisher = None
        elif pub_id:
            article.publisher_id = pub_id

        article.approved = False
        article.save()
        messages.success(request, "Article updated!")
        return redirect("index")

    editors = User.objects.filter(role="EDITOR")
    return render(
        request, "edit_article.html", {"article": article, "editors": editors}
    )


@login_required
@user_passes_test(is_staff_member)
def delete_article(request, article_id):
    """Allow authors or editors to remove an article from the system."""
    article = get_object_or_404(Article, id=article_id)
    if request.user == article.author or request.user.role == "EDITOR":
        article.delete()
        messages.success(request, "Article deleted.")
    return redirect("index")


#  NEWSLETTER LOGIC


def newsletter_list(request):
    """Display all available newsletters to the user."""
    newsletters = Newsletter.objects.all().order_by("-created_at")
    return render(request, "newsletter_list.html",
                  {"newsletters": newsletters})


def newsletter_detail(request, newsletter_id):
    """Display the details and articles within a specific newsletter."""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    can_edit = is_staff_member(request.user)
    return render(
        request,
        "newsletter_detail.html",
        {"newsletter": newsletter, "can_edit": can_edit},
    )


@login_required
@user_passes_test(is_staff_member)
def edit_newsletter(request, newsletter_id=None):
    """Handle both the creation of new newsletters and
    editing of existing ones."""
    newsletter = None
    if newsletter_id:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)

    if request.method == "POST":
        title = request.POST.get("title")
        desc = request.POST.get("description")
        a_ids = request.POST.getlist("articles")

        if not newsletter:
            newsletter = Newsletter.objects.create(
                title=title, description=desc, author=request.user
            )
        else:
            newsletter.title, newsletter.description = title, desc
            newsletter.save()

        newsletter.articles.set(a_ids)
        messages.success(request, "Newsletter saved!")
        return redirect("newsletter_detail", newsletter_id=newsletter.id)

    articles = Article.objects.filter(approved=True)
    return render(
        request,
        "edit_newsletter.html",
        {"newsletter": newsletter, "articles": articles},
    )


@login_required
@user_passes_test(is_staff_member)
def delete_newsletter(request, newsletter_id):
    """Allow authors or editors to delete a newsletter."""
    newsletter = get_object_or_404(Newsletter, id=newsletter_id)
    if request.user == newsletter.author or request.user.role == "EDITOR":
        newsletter.delete()
        messages.success(request, "Newsletter deleted.")
    return redirect("newsletter_list")


# COMMENTS & AUTH


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
    """Log out the current user and flush the session data."""
    logout(request)
    request.session.flush()
    return redirect("index")


class RegistrationForm(forms.ModelForm):
    """Form for Publishing House registration with role selection."""

    ROLE_CHOICES = [
        ('READER', 'Reader'),
        ('JOURNALIST', 'Journalist'),
        ('EDITOR', 'Editor'),
    ]

    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select,
        label="Select Your Role"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']


def register(request):
    """
    Handle the registration of Readers, Journalists, and Editors.
    Saves the user to the MySQL database and logs them in.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Hash the password for security
            user.set_password(form.cleaned_data['password'])
            # Save the role from the dropdown selection
            user.role = form.cleaned_data['role']
            user.save()

            login(request, user)
            messages.success(
                request,
                (
                    f"Welcome to The Daily Journalist, "
                    f"{user.username}!"
                )
            )
            return redirect('index')
    else:
        form = RegistrationForm()

    return render(request, 'register.html',
                  {'form': form})


@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    """Display all articles written by the logged-in journalist."""
    my_articles = Article.objects.filter(author=request.user).order_by
    ("-created_at")
    return render(request, "journalist_dashboard.html", {"articles":
                                                         my_articles})
