"""URL definitions for the `news` app.

Maps web UI views and lightweight REST API endpoints.
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .api_views import ArticleListAPIView, ArticleDetailAPIView, UserListAPIView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='news/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('create-article/', views.create_article, name='create_article'),
    path('edit-article/<int:article_id>/', views.edit_article, name='edit_article'),
    path('delete-article/<int:article_id>/', views.delete_article, name='delete_article'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('approve-article/<int:article_id>/', views.approve_article, name='approve_article'),
    path('reject-article/<int:article_id>/', views.reject_article, name='reject_article'),
    path('pending-articles/', views.pending_articles, name='pending_articles'),
    
    # Newsletter URLs
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletter/<int:newsletter_id>/', views.newsletter_detail, name='newsletter_detail'),
    path('create-newsletter/', views.create_newsletter, name='create_newsletter'),
    path('edit-newsletter/<int:newsletter_id>/', views.edit_newsletter, name='edit_newsletter'),
    path('delete-newsletter/<int:newsletter_id>/', views.delete_newsletter, name='delete_newsletter'),
    
    # Simple API URLs
    path('api/articles/', ArticleListAPIView.as_view(), name='api-article-list'),
    path('api/articles/<int:pk>/', ArticleDetailAPIView.as_view(), name='api-article-detail'),
    path('api/users/', UserListAPIView.as_view(), name='api-user-list'),
]