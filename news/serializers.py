from rest_framework import serializers
from .models import Article, CustomUser, Publisher

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class ArticleSerializer(serializers.ModelSerializer):
    journalist = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'created_at', 
            'updated_at', 'is_approved', 'journalist', 'publisher'
        ]