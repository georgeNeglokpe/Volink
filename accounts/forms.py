from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Registration form with role selection."""
    
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        help_text='Select your role in the system'
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        help_text='Optional contact phone number'
    )
    course_department = forms.CharField(
        max_length=100,
        required=False,
        help_text='Optional course or department (for students)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role', 'phone', 'course_department', 'first_name', 'last_name')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        user.phone = self.cleaned_data.get('phone', '')
        user.course_department = self.cleaned_data.get('course_department', '')
        if commit:
            user.save()
        return user

