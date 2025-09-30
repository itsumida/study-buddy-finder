from django import forms
from .models import (
    Profile, Course, Review, Message
)
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProfileAddForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={
            'required': 'Please select at least one course.'
        }
    )
    
    class Meta:
        model = Profile
        fields = [
            "major", "fname", "lname",
            "bio", "courses"
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Tell us about yourself and your study preferences...'
            })
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class ProfileEditForm(forms.ModelForm):
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
        }),
        required=False
    )
    fname = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    lname = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Tell us about yourself...',
        'rows': 3
    }), required=False)
    major = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your major'
    }), required=False)
    
    
    def clean_email(self):
        email = self.cleaned_data['email']
        pattern = r'^s\d{7}@bi\.no$'
        if not re.match(pattern, email):
            raise forms.ValidationError("Only valid BI emails allowed (e.g., s1234567@bi.no).")
        return email
    
    class Meta:
        model = Profile
        fields = ['fname', 'lname', 'bio', 'major', 'courses']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your message here...'}),
        }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your feedback...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].required = False 


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


    


