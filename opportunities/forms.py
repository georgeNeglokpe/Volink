from django import forms
from .models import Opportunity, Application
from organisations.models import Organisation


class OpportunityForm(forms.ModelForm):
    """Form for creating/editing opportunities."""
    
    class Meta:
        model = Opportunity
        fields = [
            'title', 'description', 'location', 'category',
            'required_skills', 'min_hours_per_week',
            'start_date', 'end_date', 'is_remote', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'required_skills': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_org_admin():
            # Filter organisations to only those managed by this user
            self.fields['organisation'] = forms.ModelChoiceField(
                queryset=Organisation.objects.filter(admin=user),
                required=True
            )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError('End date must be after start date.')
        
        min_hours = cleaned_data.get('min_hours_per_week')
        if min_hours is not None and min_hours < 0:
            raise forms.ValidationError('Minimum hours per week must be non-negative.')
        
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    """Form for applying to an opportunity."""
    
    class Meta:
        model = Application
        fields = []  # No fields needed, just create the application

