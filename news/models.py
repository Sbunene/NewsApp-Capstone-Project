from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    # Role choices
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
    name = models.CharField(max_length=200)
    editors = models.ManyToManyField(CustomUser, limit_choices_to={'role': 'EDITOR'}, related_name='publisher_editors')
    journalists = models.ManyToManyField(CustomUser, limit_choices_to={'role': 'JOURNALIST'}, related_name='publisher_journalists')
    
    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    journalist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'JOURNALIST'})
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']  # Newest articles first
    
    def __str__(self):
        return self.title

class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    journalist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'JOURNALIST'})
    
    def __str__(self):
        return self.title