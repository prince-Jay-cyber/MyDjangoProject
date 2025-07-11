# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Application
from .models import Profile, Job
from .models import Subscriber
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from .models import Profile
from django import forms


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'photo', 'bio', 'resume_file', 'role']

class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )

    class Meta:
        model = User
        fields = ['username']


class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        label="Bio",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us a bit about yourself...',
            'rows': 4,
        })
    )

    photo = forms.ImageField(
        label="Profile Photo",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    phone = forms.CharField(
        label="Phone Number",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +2348000000000'
        })
    )

    resume_file = forms.FileField(
        label="Upload Resume (PDF/DOC)",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'phone', 'resume_file']


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

class EmployerSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['company_name', 'logo']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message', 'cv']

    def clean_cv(self):
        cv = self.cleaned_data.get('cv')

        if not cv:
            raise forms.ValidationError("Please upload your CV.")

        # File size limit (2MB)
        if cv.size > 2 * 1024 * 1024:
            raise forms.ValidationError("CV file size should not exceed 2MB.")

        # File type validation
        valid_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if cv.content_type not in valid_types:
            raise forms.ValidationError("Only PDF, DOC, or DOCX files are allowed.")

        return cv

class JobFilterForm(forms.Form):
    keyword = forms.CharField(required=False, label='Keyword')
    location = forms.CharField(required=False)
    category = forms.CharField(required=False)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, initial=False)

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'category']
        exclude = ['employer']  # Don't show employer field in the form
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Job Description'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
        }

class JobAlertForm(forms.Form):
    subject = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}))


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your email',
                'required': 'required',
            }),
        }
