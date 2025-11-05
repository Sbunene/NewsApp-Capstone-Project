"""Django management command to create user groups and assign permissions.

This command sets up the three core user groups (Reader, Journalist, Editor)
with appropriate permissions based on their roles. Run this command after
initial migrations to establish the role-based access control system.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import CustomUser, Article, Newsletter, Publisher


class Command(BaseCommand):
    """Management command to create default user groups with permissions.
    
    Creates three user groups and assigns appropriate permissions:
        - Reader: Can view articles and newsletters
        - Journalist: Can create, edit, delete, and view their own content
        - Editor: Can approve, edit, delete, and view all content
        
    Usage:
        python manage.py create_groups
        
    Raises:
        django.contrib.auth.models.Permission.DoesNotExist: If required
            permissions are not found (should not occur after migrations).
    """
    help = 'Creates default groups (Reader, Journalist, Editor) and assigns permissions'

    def handle(self, *args, **options):
        """Execute the command to create groups and assign permissions.
        
        Args:
            *args: Unused positional arguments
            **options: Unused keyword arguments from command line
            
        Returns:
            None. Outputs success messages to stdout.
            
        Side Effects:
            Creates or updates Reader, Journalist, and Editor groups in database.
            Assigns permissions to each group based on their role requirements.
        """
        # Get content types for our models
        user_content_type = ContentType.objects.get_for_model(CustomUser)
        article_content_type = ContentType.objects.get_for_model(Article)
        newsletter_content_type = ContentType.objects.get_for_model(Newsletter)
        publisher_content_type = ContentType.objects.get_for_model(Publisher)
        
        # Create Reader Group
        reader_group, created = Group.objects.get_or_create(name='Reader')
        reader_permissions = [
            Permission.objects.get(codename='view_article', content_type=article_content_type),
            Permission.objects.get(codename='view_newsletter', content_type=newsletter_content_type),
        ]
        reader_group.permissions.set(reader_permissions)
        
        # Create Journalist Group
        journalist_group, created = Group.objects.get_or_create(name='Journalist')
        journalist_permissions = [
            Permission.objects.get(codename='add_article', content_type=article_content_type),
            Permission.objects.get(codename='change_article', content_type=article_content_type),
            Permission.objects.get(codename='delete_article', content_type=article_content_type),
            Permission.objects.get(codename='view_article', content_type=article_content_type),
            Permission.objects.get(codename='add_newsletter', content_type=newsletter_content_type),
            Permission.objects.get(codename='change_newsletter', content_type=newsletter_content_type),
            Permission.objects.get(codename='delete_newsletter', content_type=newsletter_content_type),
            Permission.objects.get(codename='view_newsletter', content_type=newsletter_content_type),
        ]
        journalist_group.permissions.set(journalist_permissions)
        
        # Create Editor Group
        editor_group, created = Group.objects.get_or_create(name='Editor')
        editor_permissions = [
            Permission.objects.get(codename='change_article', content_type=article_content_type),
            Permission.objects.get(codename='delete_article', content_type=article_content_type),
            Permission.objects.get(codename='view_article', content_type=article_content_type),
            Permission.objects.get(codename='change_newsletter', content_type=newsletter_content_type),
            Permission.objects.get(codename='delete_newsletter', content_type=newsletter_content_type),
            Permission.objects.get(codename='view_newsletter', content_type=newsletter_content_type),
        ]
        editor_group.permissions.set(editor_permissions)
        
        self.stdout.write(self.style.SUCCESS('Groups and permissions created successfully!'))
        self.stdout.write(f"Reader group has {reader_group.permissions.count()} permissions")
        self.stdout.write(f"Journalist group has {journalist_group.permissions.count()} permissions")
        self.stdout.write(f"Editor group has {editor_group.permissions.count()} permissions")