from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=32,widget=forms.TextInput(attrs={'placeholder': 'Ex: John'}))
    last_name = forms.CharField(max_length=32,widget=forms.TextInput(attrs={'placeholder': 'Ex: West'}))
    email = forms.EmailField(max_length=64,widget=forms.TextInput(attrs={'placeholder': 'Ex: johnwest@gmail.com'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']


class PostForm(forms.ModelForm):
    description = forms.CharField(max_length=255, widget=forms.Textarea(attrs={'placeholder': 'Whats on your mind?'}))
    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        labels = {
            'image': 'Image',
            'description': 'Description'
        }
        fields = ['image', 'description']
