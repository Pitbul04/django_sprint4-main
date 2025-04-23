from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm


from .models import Post, Comment


User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = (
            'title', 'text', 'pub_date', 'location', 'category', 'image',
        )
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                }
            )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )


class UserEditForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )
