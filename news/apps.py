"""Django application configuration for the news app.

This module configures the 'news' Django application, including
default settings for auto-generated primary keys.
"""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration class for the news Django application.
    
    Defines application metadata and default configurations used by Django
    when the application is loaded. The default_auto_field setting ensures
    all models use BigAutoField for primary keys by default.
    
    Attributes:
        default_auto_field: Field type for auto-generated primary keys (BigAutoField)
        name: Application name used in Django's app registry ('news')
        
    Note:
        This configuration is automatically discovered by Django when the
        'news' app is listed in INSTALLED_APPS in settings.py.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    
    def ready(self):
        """Import signals when the app is ready.
        
        This method is called by Django when the application is ready.
        It imports the signals module to ensure all signal handlers are
        registered, including the post_migrate signal that creates default
        groups and permissions.
        """
        import news.signals  # noqa: F401