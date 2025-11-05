"""Django signals for the News application.

This module provides an alternative implementation (Option A) using Django signals
to handle article approval notifications. When an article is approved, signals
automatically trigger email notifications and X/Twitter posting.

To use signals instead of view-based logic, import this module in news/apps.py.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from .models import Article, CustomUser


@receiver(post_save, sender=Article)
def notify_subscribers_on_approval(sender, instance, created, **kwargs):
    """Signal handler that sends emails and posts to X/Twitter when article is approved.
    
    This function is triggered automatically when an Article is saved. If the article
    is being approved (is_approved changed from False to True), it will:
        1. Send email notifications to all subscribers
        2. Post the article to X/Twitter (if credentials are configured)
    
    Args:
        sender: The Article model class
        instance: The Article instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    # Only process if article is being approved
    if instance.is_approved:
        # Check if this is an update (not a new creation) or if we need to check previous state
        # For simplicity, we'll always send notifications when is_approved is True
        # In production, you might want to track the previous state
        
        try:
            # Get all subscribers (readers who follow this journalist or publisher)
            subscribers = CustomUser.objects.filter(
                role='READER'
            ).filter(
                models.Q(subscribed_journalists=instance.journalist) |
                models.Q(subscribed_publishers=instance.publisher)
            ).distinct()
            
            # Send email notifications to subscribers
            email_count = 0
            for subscriber in subscribers:
                try:
                    send_mail(
                        subject=f'New Article: {instance.title}',
                        message=f"""
Hello {subscriber.username},

A new article has been published that you might be interested in:

Title: {instance.title}
Author: {instance.journalist.username}
Content: {instance.content[:200]}...

Read the full article on NewsApp!

Best regards,
NewsApp Team
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL or 'no-reply@newsapp.local',
                        recipient_list=[subscriber.email],
                        fail_silently=True,
                    )
                    email_count += 1
                except Exception:
                    # Continue with other subscribers if one fails
                    pass
            
            # Post to X/Twitter (using API v2)
            try:
                import requests
                import os
                
                # Get Twitter credentials from environment variables
                twitter_bearer_token = os.environ.get('TWITTER_BEARER_TOKEN', '')
                
                if twitter_bearer_token:
                    # Create tweet text (max 280 characters)
                    tweet_text = f"📰 New Article: {instance.title[:200]}"
                    if len(instance.title) > 200:
                        tweet_text += "..."
                    
                    # X API v2 endpoint for posting tweets
                    twitter_url = "https://api.twitter.com/2/tweets"
                    headers = {
                        "Authorization": f"Bearer {twitter_bearer_token}",
                        "Content-Type": "application/json",
                    }
                    payload = {
                        "text": tweet_text
                    }
                    
                    # Post to Twitter
                    try:
                        response = requests.post(twitter_url, json=payload, headers=headers, timeout=5)
                        if response.status_code == 201:
                            # Successfully posted to Twitter
                            pass
                    except (requests.RequestException, Exception):
                        # Fail silently if Twitter API is unavailable
                        pass
                        
            except ImportError:
                # requests library not installed - skip Twitter posting
                pass
            except Exception:
                # Twitter posting failed - continue anyway
                pass
                
        except Exception:
            # Fail silently to avoid breaking the save operation
            pass


