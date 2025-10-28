from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import CustomUser, Article, Newsletter, Publisher

class Command(BaseCommand):
    help = 'Creates default groups and assigns permissions'

    def handle(self, *args, **options):
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