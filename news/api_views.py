"""API views for the News application.

Small DRF views that expose approved articles and users. Views use
simple page-number pagination suitable for demos and tests. All views require
authentication and return data in JSON format.

API Endpoints:
    /api/articles/ - List approved articles with pagination
    /api/articles/<pk>/ - Retrieve single approved article
    /api/users/ - List all users with pagination
"""

from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Article, CustomUser
from .serializers import ArticleSerializer, UserSerializer


class StandardPagination(PageNumberPagination):
    """Configure standard pagination settings for API views.
    
    Attributes:
        page_size: Number of items per page (default 10)
        page_size_query_param: Allow client to override page size
        max_page_size: Maximum allowed page size
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ArticleListAPIView(generics.ListAPIView):
    """API endpoint that lists all approved articles.
    
    Lists articles that have been approved by editors, with pagination.
    Requires authentication. Articles include nested journalist and 
    publisher information through serializer relationships.
    
    GET Parameters:
        page: Page number (default 1)
        page_size: Number of articles per page (default 10, max 100)
    
    Returns:
        Paginated list of approved articles in JSON format
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Article.objects.filter(is_approved=True)


class ArticleDetailAPIView(generics.RetrieveAPIView):
    """API endpoint that returns a single approved article.
    
    Retrieves a specific approved article by ID. Returns 404 if the article
    doesn't exist or hasn't been approved yet. Requires authentication.
    
    URL Parameters:
        pk: Primary key (ID) of the article to retrieve
        
    Returns:
        Single article object with nested journalist/publisher data
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.filter(is_approved=True)


class UserListAPIView(generics.ListAPIView):
    """API endpoint that lists all users (paginated).
    
    Lists all users in the system with pagination. Requires authentication.
    User objects include basic profile information and role.
    
    GET Parameters:
        page: Page number (default 1)
        page_size: Number of users per page (default 10, max 100)
        
    Returns:
        Paginated list of users in JSON format
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    pagination_class = StandardPagination