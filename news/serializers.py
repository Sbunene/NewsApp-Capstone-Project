"""Serializers for the News application API.

These serializers are used by the DRF views to expose Article and User
data. They are intentionally read-only for nested relations to avoid
unexpected updates through nested payloads.
"""

from rest_framework import serializers
from .models import Article, CustomUser, Publisher


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user information for API responses.
    
    This serializer provides read-only user data including username, email,
    and role. It's used in nested relationships within ArticleSerializer to
    show journalist information without exposing sensitive data.
    
    Fields:
        id: User's unique identifier
        username: User's username
        email: User's email address
        role: User's role (READER, JOURNALIST, or EDITOR)
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher information for API responses.
    
    Provides basic publisher data for use in article listings. This is a
    read-only serializer used in nested relationships.
    
    Fields:
        id: Publisher's unique identifier
        name: Publisher's display name
    """
    class Meta:
        model = Publisher
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize Article with nested journalist and publisher data.
    
    This serializer provides complete article information including nested
    journalist and publisher objects. It's used by the API views to return
    article data in a structured format.
    
    The nested relationships (journalist, publisher) are read-only to prevent
    accidental updates through nested payloads. Article creation and updates
    should be done through the web interface.
    
    Fields:
        id: Article's unique identifier
        title: Article headline
        content: Full article text
        created_at: Timestamp when article was created
        updated_at: Timestamp when article was last modified
        is_approved: Whether the article has been approved by an editor
        journalist: Nested UserSerializer with journalist information
        publisher: Nested PublisherSerializer with publisher information
    """
    journalist = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'created_at',
            'updated_at', 'is_approved', 'journalist', 'publisher'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']