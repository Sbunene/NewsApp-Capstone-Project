"""Forms used by the News app.

This module exposes a custom user creation form and an Article form.
The ArticleForm accepts an optional `request` kwarg so that the
form.save() can set the article.journalist from the currently logged
in user instead of relying on the view to assign it.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Publisher, Newsletter


class CustomUserCreationForm(UserCreationForm):
    """User registration form with role-based access control.
    
    This form extends Django's UserCreationForm to include role selection
    and email validation. Users can register as:
    - Reader: Can view approved articles and subscribe to journalists
    - Journalist: Can create articles and newsletters
    - Editor: Can approve/reject articles and manage content
    
    The form automatically assigns users to the appropriate permission group
    based on their selected role when saved.
    
    Attributes:
        role: ChoiceField for selecting user role (default: READER)
        email: EmailField for user's email address (required)
    """
    ROLE_CHOICES = [
        ('READER', 'Reader'),
        ('JOURNALIST', 'Journalist'),
        ('EDITOR', 'Editor'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='READER',
        help_text='Select your role in the news application'
    )
    email = forms.EmailField(
        required=True,
        help_text='Enter a valid email address for notifications'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        """Save the user with role and email.
        
        The user's role determines which permission group they are assigned to.
        Group assignment happens automatically in the CustomUser.save() method.
        
        Args:
            commit: If True, save the user to the database
            
        Returns:
            CustomUser: The created user instance
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()  # This triggers group assignment in CustomUser.save()
        return user


class ArticleForm(forms.ModelForm):
    """Form to create/edit an Article.

    When the view passes the current `request` to the form via the
    `request` keyword argument, the `save()` method will assign
    `article.journalist = request.user` automatically.
    """

    class Meta:
        model = Article
        fields = ('title', 'content', 'publisher')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Write your article content here...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter article title...'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['publisher'].queryset = Publisher.objects.all()
        self.fields['publisher'].required = False

    def save(self, commit=True):
        article = super().save(commit=False)
        if self.request:
            article.journalist = self.request.user
        if commit:
            article.save()
        return article


class NewsletterForm(forms.ModelForm):
    """Form to create/edit a Newsletter.
    
    Similar to ArticleForm, accepts an optional `request` kwarg to
    automatically assign the journalist field from the logged-in user.
    """
    
    class Meta:
        model = Newsletter
        fields = ('title', 'content')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Write your newsletter content here...'}),
            'title': forms.TextInput(attrs={'placeholder': 'Enter newsletter title...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        newsletter = super().save(commit=False)
        if self.request:
            newsletter.journalist = self.request.user
        if commit:
            newsletter.save()
        return newsletter


class PublisherForm(forms.ModelForm):
    """Form to create or edit a Publisher (publishing house).

    Editors should be able to create publishers. When created the view
    may add the current editor as one of the publisher's editors.
    """

    class Meta:
        model = Publisher
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter publishing house name...'}),
        }