"""Admin registration for News models.

This file registers the CustomUser and content models with the
admin site and provides a small customization for the user admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter


# Customize how users appear in admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
        ('Reader Subscriptions', {'fields': ('subscribed_publishers', 'subscribed_journalists')}),
        ('Journalist Content', {'fields': ('published_articles', 'published_newsletters')}),
    )


# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)