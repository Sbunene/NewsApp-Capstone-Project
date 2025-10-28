from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Article, CustomUser
from .serializers import ArticleSerializer, UserSerializer

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticleListAPIView(generics.ListAPIView):
    """
    API endpoint that lists all approved articles
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Article.objects.filter(is_approved=True)

class ArticleDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint that returns a single article
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.filter(is_approved=True)

class UserListAPIView(generics.ListAPIView):
    """
    API endpoint that lists all users
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    pagination_class = StandardPagination