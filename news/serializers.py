"""Serializers for the News application API.

These serializers are used by the DRF views to expose Article and User
data. They are intentionally read-only for nested relations to avoid
unexpected updates through nested payloads.
"""

from rest_framework import serializers
from .models import Article, CustomUser, Publisher


class UserSerializer(serializers.ModelSerializer):
    """Serialize basic user information used in article listings."""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize minimal publisher information."""
    class Meta:
        model = Publisher
        fields = ['id', 'name']


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize Article including nested journalist and publisher."""
    journalist = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'created_at',
            'updated_at', 'is_approved', 'journalist', 'publisher'
        ]