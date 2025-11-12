"""Views for the News app.

This module contains the primary views used by the news application
including registration, dashboard and article CRUD operations.

The views expect a `CustomUser` with a `role` attribute which controls
access to certain features (READER, JOURNALIST, EDITOR).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CustomUser, Article, Publisher, Newsletter
from .forms import ArticleForm, CustomUserCreationForm, NewsletterForm, PublisherForm
from django.core.mail import send_mail
from django.conf import settings
from django.db import models

def register(request):
    """Register a new user with role-based setup.
    
    Handles user registration with custom fields for role selection.
    Validates email uniqueness and password strength.
    
    Returns:
        On GET: Registration form
        On POST: Redirects to dashboard on success, or shows form with errors
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(
                    request,
                    f'Registration successful! Welcome {user.username}. '
                    f'You are registered as a {user.get_role_display()}.'
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(
                    request,
                    'Registration failed. Please try again or contact support.'
                )
    else:
        form = CustomUserCreationForm()
    return render(request, 'news/register.html', {'form': form})

@login_required
def dashboard(request):
    """Display user's dashboard based on their role.
    
    Shows different content for Readers (approved articles),
    Journalists (their articles), and Editors (pending articles).
    Includes role-specific permissions and actions.
    
    Returns:
        Rendered dashboard template with role-specific context
    """
    user = request.user
    context = {
        'user': user,
        'user_groups': list(user.groups.all()),
        'user_permissions': list(user.get_all_permissions()),
    }
    
    try:
        # Different content based on role with error handling and optimized queries
        if user.role == 'READER':
            context['message'] = 'Welcome Reader! Browse our latest news.'
            # Optimize with select_related to reduce database queries
            context['articles'] = Article.objects.filter(
                is_approved=True
            ).select_related('journalist', 'publisher').order_by('-created_at')
            # Only fetch newsletters from subscribed journalists
            context['newsletters'] = Newsletter.objects.filter(
                journalist__in=user.subscribed_journalists.all()
            ).select_related('journalist').order_by('-created_at')[:5]
        elif user.role == 'JOURNALIST':
            context['message'] = 'Welcome Journalist! Create and manage your articles and newsletters.'
            # Optimize with select_related for publisher
            context['articles'] = Article.objects.filter(
                journalist=user
            ).select_related('publisher').order_by('-created_at')
            context['newsletters'] = Newsletter.objects.filter(
                journalist=user
            ).order_by('-created_at')[:5]
        elif user.role == 'EDITOR':
            context['message'] = 'Welcome Editor! Review and approve articles.'
            # Show pending articles with related journalist and publisher data
            context['pending_articles'] = Article.objects.filter(
                is_approved=False
            ).select_related('journalist', 'publisher').order_by('-created_at')
            context['newsletters'] = Newsletter.objects.all().select_related(
                'journalist'
            ).order_by('-created_at')[:5]
        else:
            messages.warning(request, 'Your account has no role assigned. Please contact support.')
            context['message'] = 'Account configuration needed'
            context['articles'] = []
    except Exception as e:
        messages.error(request, 'Error loading dashboard content. Please try again later.')
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error for user {user.username}: {str(e)}")
        context['articles'] = []
        context['newsletters'] = []
    
    return render(request, 'news/dashboard.html', context)

@login_required
@permission_required('news.add_article', raise_exception=True)
def create_article(request):
    """Create a new Article.

    This view uses `ArticleForm`. The form accepts an optional `request`
    kwarg; when provided the form.save() will set the journalist field
    to the current user. We prefer that approach so the form encapsulates
    the assignment logic.
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST, request=request)
        if form.is_valid():
            article = form.save()
            messages.success(request, 'Article submitted for approval!')
            return redirect('dashboard')
    else:
        form = ArticleForm(request=request)
    return render(request, 'news/create_article.html', {'form': form})


@login_required
def create_publisher(request):
    """Create a new Publisher (publishing house).

    Only users with the EDITOR role can create a publishing house. The
    creating editor is automatically added to the publisher's editors.
    """
    if request.user.role != 'EDITOR':
        messages.error(request, 'Only editors can create a publishing house.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            publisher = form.save()
            # Add the current user as one of the publisher's editors
            publisher.editors.add(request.user)
            messages.success(request, f'Publishing house "{publisher.name}" created.')
            return redirect('dashboard')
    else:
        form = PublisherForm()

    return render(request, 'news/create_publisher.html', {'form': form})

@login_required
@permission_required('news.change_article', raise_exception=True)
def approve_article(request, article_id):
    """Approve an article and notify subscribers.
    
    Editors can approve articles which makes them visible to readers.
    Sends email notifications to subscribers of the journalist/publisher.
    Handles various error cases gracefully.
    
    Args:
        article_id: ID of the article to approve
        
    Returns:
        Redirects to dashboard with success/error message
    """
    try:
        article = get_object_or_404(Article, id=article_id)
        
        if not request.user.role == 'EDITOR':
            messages.error(request, 'Only editors can approve articles.')
            return redirect('dashboard')

        # Editors can approve pending articles. We keep this broad so that
        # editors can manage pending content across publishers within the app.
            
        if article.is_approved:
            messages.info(request, f'Article "{article.title}" was already approved.')
            return redirect('dashboard')
            
        article.is_approved = True
        article.save()
        
        # Send email notification to subscribers
        try:
            # Get all subscribers (readers who follow this journalist or publisher)
            subscribers = CustomUser.objects.filter(
                role='READER'
            ).filter(
                models.Q(subscribed_journalists=article.journalist) |
                models.Q(subscribed_publishers=article.publisher)
            ).distinct()
            
            for subscriber in subscribers:
                send_mail(
                    subject=f'New Article: {article.title}',
                    message=f"""
                Hello {subscriber.username},

                A new article has been published that you might be interested in:

                Title: {article.title}
                Author: {article.journalist.username}
                Content: {article.content[:200]}...

                Read the full article on NewsApp!

                Best regards,
                NewsApp Team
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL or 'no-reply@newsapp.local',
                    recipient_list=[subscriber.email],
                    fail_silently=True,
                )
            
            messages.success(
                request,
                f'Article "{article.title}" approved and {subscribers.count()} '
                f'subscriber(s) notified!'
            )
        except Exception as e:
            messages.warning(
                request,
                f'Article "{article.title}" approved but email notifications '
                f'failed: {str(e)}'
            )
            
    except Article.DoesNotExist:
        messages.error(request, f'Article with ID {article_id} not found.')
    except Exception as e:
        messages.error(
            request,
            f'Error approving article: {str(e)}. Please try again or contact support.'
        )
        
    return redirect('dashboard')

@login_required
@permission_required('news.change_article', raise_exception=True)
def reject_article(request, article_id):
    """Reject and delete an article.
    
    Only editors can reject articles. When an article is rejected,
    it is permanently deleted from the system.
    
    Args:
        article_id: ID of the article to reject
        
    Returns:
        Redirects to dashboard with success/error message
    """
    try:
        article = get_object_or_404(Article, id=article_id)
        
        if not request.user.role == 'EDITOR':
            messages.error(request, 'Only editors can reject articles.')
            return redirect('dashboard')
        
        title = article.title
        article.delete()
        messages.success(request, f'Article "{title}" has been rejected and deleted.')
        
    except Article.DoesNotExist:
        messages.error(request, f'Article with ID {article_id} not found.')
    except Exception as e:
        messages.error(
            request,
            f'Error rejecting article: {str(e)}. Please try again or contact support.'
        )
    
    return redirect('dashboard')

@login_required
def pending_articles(request):
    """Display a list of articles pending approval.
    
    Only editors can access this view. Shows all articles that have not
    yet been approved for publication.
    
    Returns:
        On success: Renders pending_articles.html with list of unapproved articles
        On error: Redirects to dashboard with error message
    """
    try:
        if request.user.role != 'EDITOR':
            messages.error(request, 'Access denied. Only editors can view pending articles.')
            return redirect('dashboard')
        pending_articles = Article.objects.filter(is_approved=False).select_related('journalist', 'publisher')
        
        return render(
            request,
            'news/pending_articles.html',
            {'pending_articles': pending_articles}
        )
        
    except Exception as e:
        messages.error(
            request,
            f'Error retrieving pending articles: {str(e)}. Please try again.'
        )
        return redirect('dashboard')

@login_required
@permission_required('news.change_article', raise_exception=True)
def edit_article(request, article_id):
    """Edit an existing article.
    
    Journalists can only edit their own articles. Editors can edit any article.
    Uses ArticleForm to validate and save changes.
    
    Args:
        article_id: ID of the article to edit
        
    Returns:
        On GET: Rendered edit form
        On POST: Redirects to dashboard on success
        On error: Redirects to dashboard with error message
    """
    try:
        article = get_object_or_404(Article, id=article_id)
        
        # Ensure journalists can only edit their own articles
        if request.user.role == 'JOURNALIST' and article.journalist != request.user:
            messages.error(request, 'You can only edit your own articles.')
            return redirect('dashboard')

        # Editors can edit any article; journalists are restricted to their own articles.
        
        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=article, request=request)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    f'Article "{article.title}" updated successfully!'
                )
                return redirect('dashboard')
        else:
            form = ArticleForm(instance=article, request=request)
        
        return render(
            request,
            'news/edit_article.html',
            {'form': form, 'article': article}
        )
        
    except Article.DoesNotExist:
        messages.error(request, f'Article with ID {article_id} not found.')
    except Exception as e:
        messages.error(
            request,
            f'Error editing article: {str(e)}. Please try again or contact support.'
        )
    return redirect('dashboard')

@login_required
@permission_required('news.delete_article', raise_exception=True)
def delete_article(request, article_id):
    """Delete an article.
    
    Journalists can only delete their own articles. Editors can delete any article.
    Requires confirmation via POST request for actual deletion.
    
    Args:
        article_id: ID of the article to delete
        
    Returns:
        On GET: Renders delete confirmation page
        On POST: Redirects to dashboard after deletion
        On error: Redirects to dashboard with error message
    """
    try:
        article = get_object_or_404(Article, id=article_id)
        
        # Ensure journalists can only delete their own articles
        if request.user.role == 'JOURNALIST' and article.journalist != request.user:
            messages.error(request, 'You can only delete your own articles.')
            return redirect('dashboard')

        # Editors can delete any article; journalists are restricted to their own articles.
        
        if request.method == 'POST':
            article_title = article.title
            article.delete()
            messages.success(
                request,
                f'Article "{article_title}" has been permanently deleted.'
            )
            return redirect('dashboard')
        
        return render(
            request,
            'news/delete_article.html',
            {'article': article}
        )
        
    except Article.DoesNotExist:
        messages.error(request, f'Article with ID {article_id} not found.')
    except Exception as e:
        messages.error(
            request,
            f'Error deleting article: {str(e)}. Please try again or contact support.'
        )
    return redirect('dashboard')

@login_required
def article_detail(request, article_id):
    """Display detailed view of a single article.
    
    Access rules:
    - Readers can only view approved articles
    - Journalists can view their own articles (approved or not) and all approved articles
    - Editors can view all articles
    
    Args:
        article_id: ID of the article to display
        
    Returns:
        On success: Renders article_detail.html with article data
        On error/no access: Redirects to dashboard with message
    """
    try:
        article = get_object_or_404(Article, id=article_id)
        
        # Only show approved articles to readers
        if not article.is_approved and request.user.role == 'READER':
            messages.error(
                request,
                'This article is not yet available for viewing.'
            )
            return redirect('dashboard')
        
        # Journalists can only see their own unapproved articles
        if (request.user.role == 'JOURNALIST' and 
            article.journalist != request.user and 
            not article.is_approved):
            messages.error(
                request,
                'You can only view your own unpublished articles.'
            )
            return redirect('dashboard')
        
        return render(
            request,
            'news/article_detail.html',
            {'article': article}
        )
        
    except Article.DoesNotExist:
        messages.error(request, f'Article with ID {article_id} not found.')
    except Exception as e:
        messages.error(
            request,
            f'Error retrieving article: {str(e)}. Please try again.'
        )
    return redirect('dashboard')

# Newsletter Views

@login_required
def newsletter_list(request):
    """Display list of newsletters based on user role.
    
    Readers see all newsletters from subscribed journalists.
    Journalists see their own newsletters.
    Editors see all newsletters.
    
    Returns:
        Rendered newsletter_list.html with appropriate newsletters
    """
    user = request.user
    
    try:
        if user.role == 'READER':
            newsletters = Newsletter.objects.filter(
                journalist__in=user.subscribed_journalists.all()
            ).select_related('journalist').order_by('-created_at')
        elif user.role == 'JOURNALIST':
            newsletters = Newsletter.objects.filter(
                journalist=user
            ).order_by('-created_at')
        elif user.role == 'EDITOR':
            newsletters = Newsletter.objects.all().select_related(
                'journalist'
            ).order_by('-created_at')
        else:
            newsletters = []
        
        return render(
            request,
            'news/newsletter_list.html',
            {'newsletters': newsletters}
        )
    except Exception as e:
        messages.error(request, f'Error loading newsletters: {str(e)}')
        return redirect('dashboard')

@login_required
def newsletter_detail(request, newsletter_id):
    """Display detailed view of a single newsletter.
    
    Args:
        newsletter_id: ID of the newsletter to display
        
    Returns:
        On success: Renders newsletter_detail.html
        On error/no access: Redirects to newsletter list with message
    """
    try:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        user = request.user
        
        if user.role == 'READER':
            if newsletter.journalist not in user.subscribed_journalists.all():
                messages.error(request, 'You can only view newsletters from journalists you subscribe to.')
                return redirect('newsletter_list')
        elif user.role == 'JOURNALIST':
            if newsletter.journalist != user:
                messages.error(request, 'You can only view your own newsletters.')
                return redirect('newsletter_list')
        
        return render(request, 'news/newsletter_detail.html', {'newsletter': newsletter})
    except Newsletter.DoesNotExist:
        messages.error(request, f'Newsletter with ID {newsletter_id} not found.')
    except Exception as e:
        messages.error(request, f'Error retrieving newsletter: {str(e)}')
    return redirect('newsletter_list')

@login_required
@permission_required('news.add_newsletter', raise_exception=True)
def create_newsletter(request):
    """Create a new Newsletter (Journalists only)."""
    if request.user.role != 'JOURNALIST':
        messages.error(request, 'Only journalists can create newsletters.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST, request=request)
        if form.is_valid():
            newsletter = form.save()
            messages.success(request, f'Newsletter "{newsletter.title}" created successfully!')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm(request=request)
    
    return render(request, 'news/create_newsletter.html', {'form': form})

@login_required
@permission_required('news.change_newsletter', raise_exception=True)
def edit_newsletter(request, newsletter_id):
    """Edit an existing newsletter."""
    try:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        
        if request.user.role == 'JOURNALIST' and newsletter.journalist != request.user:
            messages.error(request, 'You can only edit your own newsletters.')
            return redirect('newsletter_list')
        
        if request.method == 'POST':
            form = NewsletterForm(request.POST, instance=newsletter, request=request)
            if form.is_valid():
                form.save()
                messages.success(request, f'Newsletter "{newsletter.title}" updated successfully!')
                return redirect('newsletter_list')
        else:
            form = NewsletterForm(instance=newsletter, request=request)
        
        return render(request, 'news/edit_newsletter.html', {'form': form, 'newsletter': newsletter})
    except Newsletter.DoesNotExist:
        messages.error(request, f'Newsletter with ID {newsletter_id} not found.')
    except Exception as e:
        messages.error(request, f'Error editing newsletter: {str(e)}')
    return redirect('newsletter_list')

@login_required
@permission_required('news.delete_newsletter', raise_exception=True)
def delete_newsletter(request, newsletter_id):
    """Delete a newsletter."""
    try:
        newsletter = get_object_or_404(Newsletter, id=newsletter_id)
        
        if request.user.role == 'JOURNALIST' and newsletter.journalist != request.user:
            messages.error(request, 'You can only delete your own newsletters.')
            return redirect('newsletter_list')
        
        if request.method == 'POST':
            newsletter_title = newsletter.title
            newsletter.delete()
            messages.success(request, f'Newsletter "{newsletter_title}" has been permanently deleted.')
            return redirect('newsletter_list')
        
        return render(request, 'news/delete_newsletter.html', {'newsletter': newsletter})
    except Newsletter.DoesNotExist:
        messages.error(request, f'Newsletter with ID {newsletter_id} not found.')
    except Exception as e:
        messages.error(request, f'Error deleting newsletter: {str(e)}')
    return redirect('newsletter_list')