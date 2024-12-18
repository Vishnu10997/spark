from django import forms
from django.contrib.auth.models import User
from .models import profile1

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = profile1
        fields = ['name', 'bio', 'location', 'photo1', 'photo2', 'photo3', 
                  'interest1', 'interest2', 'interest3', 'interest4', 'interest5']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'photo1': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'photo2': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'photo3': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
