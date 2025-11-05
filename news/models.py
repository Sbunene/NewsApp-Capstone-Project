"""Data models for the News application.

Includes a custom user model with roles and models for Publisher,
Article and Newsletter.
"""

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with role-based permissions and relationships.
    
    This model extends Django's AbstractUser to add role-based access control
    and relationships between users (reader subscriptions, journalist articles).
    Users are automatically assigned to groups based on their role.
    
    Attributes:
        ROLE_CHOICES: List of valid roles (READER, JOURNALIST, EDITOR)
        role: User's role that determines permissions and features
        subscribed_publishers: M2M to publishers (readers only)
        subscribed_journalists: M2M to journalist users (readers only)
        published_articles: M2M to articles (journalists only)
        published_newsletters: M2M to newsletters (journalists only)
    """
    
    ROLE_CHOICES = [
        ('READER', 'Reader'),
        ('JOURNALIST', 'Journalist'),
        ('EDITOR', 'Editor'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='READER')
    
    # Fields for Readers - use string references to avoid circular imports
    subscribed_publishers = models.ManyToManyField(
        'Publisher', 
        related_name='subscribers',
        blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        limit_choices_to={'role': 'JOURNALIST'}
    )
    
    # Fields for Journalists - use string references
    published_articles = models.ManyToManyField(
        'Article',
        related_name='journalist_articles',
        blank=True
    )
    published_newsletters = models.ManyToManyField(
        'Newsletter',
        related_name='journalist_newsletters',
        blank=True
    )
    
    def save(self, *args, **kwargs):
        # Check if this is a new user (has no ID yet)
        is_new = self._state.adding
        
        # First save the user to get an ID if it's new
        super().save(*args, **kwargs)
        
        # Now we can safely work with many-to-many relationships
        if self.role == 'JOURNALIST':
            if hasattr(self, 'subscribed_publishers'):
                self.subscribed_publishers.clear()
            if hasattr(self, 'subscribed_journalists'):
                self.subscribed_journalists.clear()
        elif self.role == 'READER':
            if hasattr(self, 'published_articles'):
                self.published_articles.clear()
            if hasattr(self, 'published_newsletters'):
                self.published_newsletters.clear()
        
        # Auto-assign to correct group based on role
        from django.contrib.auth.models import Group
        
        # Remove from all groups first
        self.groups.clear()
        
        # Add to appropriate group
        if self.role == 'READER':
            group, created = Group.objects.get_or_create(name='Reader')
            self.groups.add(group)
        elif self.role == 'JOURNALIST':
            group, created = Group.objects.get_or_create(name='Journalist') 
            self.groups.add(group)
        elif self.role == 'EDITOR':
            group, created = Group.objects.get_or_create(name='Editor')
            self.groups.add(group)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Publisher(models.Model):
    """Publisher organization that can have editors and journalists.
    
    Publishers represent news organizations that can publish articles.
    They have relationships to editors who can approve content and
    journalists who can write articles.
    
    Attributes:
        name: Publisher's display name
        editors: M2M to users with EDITOR role
        journalists: M2M to users with JOURNALIST role
    """
    
    name = models.CharField(
        max_length=200,
        help_text="The publisher's display name"
    )
    editors = models.ManyToManyField(
        CustomUser,
        limit_choices_to={'role': 'EDITOR'},
        related_name='publisher_editors',
        help_text="Editors who can approve content for this publisher"
    )
    journalists = models.ManyToManyField(
        CustomUser,
        limit_choices_to={'role': 'JOURNALIST'},
        related_name='publisher_journalists',
        help_text="Journalists who can write for this publisher"
    )
    
    def __str__(self):
        return self.name

class Article(models.Model):
    """News article that can be written by journalists and approved by editors.
    
    Articles are the main content type in the system. They are created by
    journalists and must be approved by editors before being visible to
    readers. Articles can optionally be associated with a publisher.
    
    Attributes:
        title: Article headline
        content: Main article text
        created_at: When the article was first created
        updated_at: When the article was last modified
        is_approved: Whether an editor has approved for publication
        journalist: User who wrote the article (must be JOURNALIST role)
        publisher: Optional publishing organization
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Article headline"
    )
    content = models.TextField(
        help_text="Main article content"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the article was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the article was last modified"
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether this article has been approved by an editor"
    )
    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'JOURNALIST'},
        help_text="The user who wrote this article"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Optional publisher this article is associated with"
    )
    
    class Meta:
        ordering = ['-created_at']  # Newest articles first
    
    def __str__(self):
        return self.title

class Newsletter(models.Model):
    """Newsletter that can be published by journalists.
    
    Newsletters are simpler than articles - they don't require approval
    and aren't associated with publishers. They provide a way for
    journalists to send updates directly to their subscribers.
    
    Attributes:
        title: Newsletter subject/headline
        content: Newsletter body content
        created_at: When the newsletter was created
        journalist: User who wrote the newsletter (must be JOURNALIST role)
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Newsletter subject/headline"
    )
    content = models.TextField(
        help_text="Newsletter body content"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this newsletter was created"
    )
    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'JOURNALIST'},
        help_text="The journalist who wrote this newsletter"
    )
    
    def __str__(self):
        return self.title