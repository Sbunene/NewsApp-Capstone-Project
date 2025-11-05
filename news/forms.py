"""Forms used by the News app.

This module exposes a custom user creation form and an Article form.
The ArticleForm accepts an optional `request` kwarg so that the
form.save() can set the article.journalist from the currently logged
in user instead of relying on the view to assign it.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Publisher


class CustomUserCreationForm(UserCreationForm):
    """A lightweight user creation form that asks for role and email."""
    ROLE_CHOICES = [
        ('READER', 'Reader'),
        ('JOURNALIST', 'Journalist'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, initial='READER')
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
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