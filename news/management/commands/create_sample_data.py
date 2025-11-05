"""Django management command to create sample data for testing.

This command populates the database with sample publishers, users (journalists
and editors), and articles (both approved and pending) for development and
testing purposes. Useful for demonstrating application functionality without
manual data entry.
"""

from django.core.management.base import BaseCommand
from news.models import CustomUser, Article, Publisher
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    """Management command to create sample data for development and testing.
    
    Creates sample publishers, test users, and articles to populate the database
    with realistic data. This allows developers to test the application without
    manually creating test data through the UI.
    
    Creates:
        - 3 publishers (Tech News Network, Sports Daily, Politics Today)
        - 2 journalists (tech_journalist, sports_journalist)
        - 1 editor (sample_editor)
        - 5 approved articles
        - 2 pending articles
        
    Usage:
        python manage.py create_sample_data
        
    Login Credentials Created:
        - tech_journalist / test123
        - sports_journalist / test123
        - sample_editor / test123
        - admin / admin123 (if created separately)
    """
    help = 'Creates sample data (publishers, users, articles) for testing'

    def handle(self, *args, **options):
        """Execute the command to create sample data.
        
        Args:
            *args: Unused positional arguments
            **options: Unused keyword arguments from command line
            
        Returns:
            None. Outputs success messages to stdout.
            
        Side Effects:
            Creates publishers, users, and articles in the database.
            Skips creation if entities with same identifiers already exist.
        """
        # Create sample publishers
        tech_publisher, created = Publisher.objects.get_or_create(name='Tech News Network')
        sports_publisher, created = Publisher.objects.get_or_create(name='Sports Daily')
        politics_publisher, created = Publisher.objects.get_or_create(name='Politics Today')
        
        # Check if sample journalist exists, if not create it
        try:
            journalist1 = CustomUser.objects.get(username='tech_journalist')
        except CustomUser.DoesNotExist:
            journalist1 = CustomUser.objects.create_user(
                username='tech_journalist',
                password='test123',
                email='tech@newsapp.com',
                role='JOURNALIST'
            )
        
        try:
            journalist2 = CustomUser.objects.get(username='sports_journalist')
        except CustomUser.DoesNotExist:
            journalist2 = CustomUser.objects.create_user(
                username='sports_journalist',
                password='test123',
                email='sports@newsapp.com',
                role='JOURNALIST'
            )
        
        # Check if sample editor exists, if not create it  
        try:
            editor = CustomUser.objects.get(username='sample_editor')
        except CustomUser.DoesNotExist:
            editor = CustomUser.objects.create_user(
                username='sample_editor',
                password='test123',
                email='editor@newsapp.com',
                role='EDITOR'
            )
        
        # Create sample approved articles
        sample_articles = [
            {
                'title': 'Breaking: New AI Technology Revolutionizes Healthcare',
                'content': 'Artificial intelligence is transforming the healthcare industry with new diagnostic tools that can detect diseases earlier and more accurately than ever before. Hospitals worldwide are adopting these technologies to improve patient outcomes.',
                'journalist': journalist1,
                'publisher': tech_publisher,
                'is_approved': True
            },
            {
                'title': 'Local Team Wins Championship After Dramatic Final',
                'content': 'In an unforgettable match that went into overtime, our local team secured the championship title with a last-minute goal. Fans celebrated throughout the night as the team brought home the trophy.',
                'journalist': journalist2,
                'publisher': sports_publisher,
                'is_approved': True
            },
            {
                'title': 'New Environmental Policy Announced by Government',
                'content': 'The government has unveiled a comprehensive new environmental policy aimed at reducing carbon emissions by 50% over the next decade. The plan includes investments in renewable energy and stricter regulations for industrial polluters.',
                'journalist': journalist1,
                'publisher': politics_publisher,
                'is_approved': True
            },
            {
                'title': 'Tech Giant Announces Revolutionary Smartphone',
                'content': 'The latest smartphone from the tech giant features groundbreaking battery technology that promises week-long battery life. Early reviews praise the innovative design and advanced camera system.',
                'journalist': journalist1,
                'publisher': tech_publisher,
                'is_approved': True
            },
            {
                'title': 'Olympic Athlete Sets New World Record',
                'content': 'In a stunning performance at the international games, the star athlete broke a world record that had stood for over a decade. The achievement marks a significant milestone in sports history.',
                'journalist': journalist2,
                'publisher': sports_publisher,
                'is_approved': True
            }
        ]
        
        # Create pending articles
        pending_articles = [
            {
                'title': 'Exclusive: Inside the Secret Space Mission',
                'content': 'Our investigative team has uncovered details about a classified space mission that could change our understanding of the universe. Sources reveal unprecedented scientific discoveries.',
                'journalist': journalist1,
                'publisher': tech_publisher,
                'is_approved': False
            },
            {
                'title': 'Controversial Trade Decision Shakes Sports World',
                'content': 'A surprising trade decision has divided experts and fans alike. The move could reshape the competitive landscape for seasons to come.',
                'journalist': journalist2,
                'publisher': sports_publisher,
                'is_approved': False
            }
        ]
        
        # Create approved articles
        for article_data in sample_articles:
            if not Article.objects.filter(title=article_data['title']).exists():
                Article.objects.create(**article_data)
        
        # Create pending articles
        for article_data in pending_articles:
            if not Article.objects.filter(title=article_data['title']).exists():
                Article.objects.create(**article_data)

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Created journalists: tech_journalist, sports_journalist')
        self.stdout.write(f'Created editor: sample_editor')
        self.stdout.write(f'Created 5 approved articles and 2 pending articles')
        self.stdout.write(f'Login credentials:')
        self.stdout.write(f'  - Reader: admin / admin123')
        self.stdout.write(f'  - Journalist 1: tech_journalist / test123')
        self.stdout.write(f'  - Journalist 2: sports_journalist / test123')
        self.stdout.write(f'  - Editor: sample_editor / test123')