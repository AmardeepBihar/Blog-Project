from django import forms
from .models import Feedback,ContactRequest

# FEEDBACK FORM
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = (
            'overall_experience', 
            'content_quality', 
            'design_quality', 
            'issue_type', 
            'description_of_issue', 
            'additional_comment',
            'blog_title_or_question'
        )
        widgets = {
            'blog_title_or_question': forms.TextInput(attrs={'class': 'form-control'}),
            'overall_experience': forms.Select(attrs={'class': 'form-control'}),
            'content_quality': forms.Select(attrs={'class': 'form-control'}),
            'design_quality': forms.Select(attrs={'class': 'form-control'}),
            'issue_type': forms.Select(attrs={'class': 'form-control'}),
            'description_of_issue': forms.Textarea(attrs={'class': 'form-control'}),
            'additional_comment': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['name', 'email', 'phone', 'subject', 'message']

        # Widgets to add the 'form-control' class
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

