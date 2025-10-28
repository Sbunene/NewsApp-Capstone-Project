from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CustomUser, Article, Publisher, Newsletter
from .forms import ArticleForm, CustomUserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.db import models

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'news/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'user_groups': list(user.groups.all()),
        'user_permissions': list(user.get_all_permissions()),
    }
    
    # Different content based on role
    if user.role == 'READER':
        context['message'] = 'Welcome Reader! Browse our latest news.'
        context['articles'] = Article.objects.filter(is_approved=True)
    elif user.role == 'JOURNALIST':
        context['message'] = 'Welcome Journalist! Create and manage your articles.'
        context['articles'] = Article.objects.filter(journalist=user)
    elif user.role == 'EDITOR':
        context['message'] = 'Welcome Editor! Review and approve articles.'
        context['pending_articles'] = Article.objects.filter(is_approved=False)
    
    return render(request, 'news/dashboard.html', context)

@login_required
@permission_required('news.add_article', raise_exception=True)
def create_article(request):
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
@permission_required('news.add_article', raise_exception=True)
def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            article.save()
            messages.success(request, 'Article submitted for approval!')
            return redirect('dashboard')
    else:
        form = ArticleForm()
    return render(request, 'news/create_article.html', {'form': form})

@login_required
@permission_required('news.change_article', raise_exception=True)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user.role == 'EDITOR':
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
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    fail_silently=True,
                )
            
            messages.success(request, f'Article "{article.title}" approved and notifications sent!')
        except Exception as e:
            messages.success(request, f'Article "{article.title}" approved! (Email notification failed: {str(e)})')
        
    else:
        messages.error(request, 'You do not have permission to approve articles.')
    return redirect('dashboard')

@login_required
@permission_required('news.change_article', raise_exception=True)
def reject_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.user.role == 'EDITOR':
        article.delete()
        messages.success(request, 'Article rejected and deleted.')
    else:
        messages.error(request, 'You do not have permission to reject articles.')
    return redirect('dashboard')

@login_required
def pending_articles(request):
    if request.user.role != 'EDITOR':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    pending_articles = Article.objects.filter(is_approved=False)
    return render(request, 'news/pending_articles.html', {'pending_articles': pending_articles})

@login_required
@permission_required('news.change_article', raise_exception=True)
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Ensure journalists can only edit their own articles
    if request.user.role == 'JOURNALIST' and article.journalist != request.user:
        messages.error(request, 'You can only edit your own articles.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully!')
            return redirect('dashboard')
    else:
        form = ArticleForm(instance=article, request=request)
    
    return render(request, 'news/edit_article.html', {'form': form, 'article': article})

@login_required
@permission_required('news.delete_article', raise_exception=True)
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Ensure journalists can only delete their own articles
    if request.user.role == 'JOURNALIST' and article.journalist != request.user:
        messages.error(request, 'You can only delete your own articles.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        article_title = article.title
        article.delete()
        messages.success(request, f'Article "{article_title}" has been deleted.')
        return redirect('dashboard')
    
    return render(request, 'news/delete_article.html', {'article': article})

@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # Only show approved articles to readers, or their own articles to journalists
    if not article.is_approved and request.user.role == 'READER':
        messages.error(request, 'This article is not available.')
        return redirect('dashboard')
    
    # Journalists can only see their own unapproved articles
    if request.user.role == 'JOURNALIST' and article.journalist != request.user and not article.is_approved:
        messages.error(request, 'You can only view your own articles.')
        return redirect('dashboard')
    
    return render(request, 'news/article_detail.html', {'article': article})