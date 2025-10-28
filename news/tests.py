from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser, Article, Publisher

class NewsAppTests(APITestCase):
    def setUp(self):
        # Create groups and assign permissions
        self.setup_groups_and_permissions()
        
        # Create test users
        self.reader = CustomUser.objects.create_user(
            username='testreader',
            password='testpass123',
            email='reader@test.com',
            role='READER'
        )
        # Manually add reader to Reader group
        reader_group = Group.objects.get(name='Reader')
        self.reader.groups.add(reader_group)
        
        self.journalist = CustomUser.objects.create_user(
            username='testjournalist',
            password='testpass123',
            email='journalist@test.com',
            role='JOURNALIST'
        )
        # Manually add journalist to Journalist group
        journalist_group = Group.objects.get(name='Journalist')
        self.journalist.groups.add(journalist_group)
        
        self.editor = CustomUser.objects.create_user(
            username='testeditor',
            password='testpass123',
            email='editor@test.com',
            role='EDITOR'
        )
        # Manually add editor to Editor group
        editor_group = Group.objects.get(name='Editor')
        self.editor.groups.add(editor_group)
        
        # Create test publisher
        self.publisher = Publisher.objects.create(name='Test Publisher')
        
        # Create test articles
        self.approved_article = Article.objects.create(
            title='Approved Test Article',
            content='This is an approved test article content.',
            journalist=self.journalist,
            publisher=self.publisher,
            is_approved=True
        )
        
        self.pending_article = Article.objects.create(
            title='Pending Test Article',
            content='This is a pending test article content.',
            journalist=self.journalist,
            publisher=self.publisher,
            is_approved=False
        )
    
    def setup_groups_and_permissions(self):
        """Set up groups and permissions for testing"""
        # Get content types
        article_content_type = ContentType.objects.get_for_model(Article)
        user_content_type = ContentType.objects.get_for_model(CustomUser)
        
        # Create or get groups
        reader_group, created = Group.objects.get_or_create(name='Reader')
        journalist_group, created = Group.objects.get_or_create(name='Journalist') 
        editor_group, created = Group.objects.get_or_create(name='Editor')
        
        # Get permissions
        view_article = Permission.objects.get(codename='view_article', content_type=article_content_type)
        add_article = Permission.objects.get(codename='add_article', content_type=article_content_type)
        change_article = Permission.objects.get(codename='change_article', content_type=article_content_type)
        delete_article = Permission.objects.get(codename='delete_article', content_type=article_content_type)
        
        # Assign permissions to groups
        reader_group.permissions.set([view_article])
        journalist_group.permissions.set([view_article, add_article, change_article, delete_article])
        editor_group.permissions.set([view_article, change_article, delete_article])
    
    def test_article_creation(self):
        """Test that journalists can create articles"""
        self.client.login(username='testjournalist', password='testpass123')
        url = reverse('create_article')
        data = {
            'title': 'New Test Article',
            'content': 'This is a new test article content.',
            'publisher': self.publisher.id
        }
        response = self.client.post(url, data)
        
        # For POST requests that might fail, let's check what's happening
        if response.status_code != 302:
            print(f"Unexpected status: {response.status_code}")
            print(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Article.objects.filter(title='New Test Article').exists())
    
    def test_article_approval(self):
        """Test that editors can approve articles"""
        self.client.login(username='testeditor', password='testpass123')
        url = reverse('approve_article', args=[self.pending_article.id])
        response = self.client.get(url)
        self.pending_article.refresh_from_db()
        self.assertTrue(self.pending_article.is_approved)
    
    def test_api_article_list(self):
        """Test that API returns only approved articles"""
        self.client.login(username='testreader', password='testpass123')
        url = reverse('api-article-list')  # Use the URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Since we have pagination, check the results array
        self.assertEqual(len(response.data['results']), 1)  # Only approved article
        self.assertEqual(response.data['results'][0]['title'], 'Approved Test Article')
    
    def test_user_permissions(self):
        """Test that users cannot access unauthorized content"""
        self.client.login(username='testreader', password='testpass123')
        
        # Readers shouldn't be able to access create article page
        url = reverse('create_article')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Permission denied
    
    def test_journalist_isolation(self):
        """Test that journalists only see their own articles"""
        # Create another journalist
        other_journalist = CustomUser.objects.create_user(
            username='otherjournalist',
            password='testpass123',
            email='other@test.com',
            role='JOURNALIST'
        )
        journalist_group = Group.objects.get(name='Journalist')
        other_journalist.groups.add(journalist_group)
        
        # Create article for other journalist
        Article.objects.create(
            title='Other Journalist Article',
            content='Content by other journalist.',
            journalist=other_journalist,
            is_approved=False
        )
        
        # Login as first journalist
        self.client.login(username='testjournalist', password='testpass123')
        url = reverse('dashboard')
        response = self.client.get(url)
        
        # Should only see their own articles
        self.assertContains(response, 'Pending Test Article')
        self.assertNotContains(response, 'Other Journalist Article')