from django import forms
from .models import Rating, Service

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating_type', 'service', 'customer_name', 'rating', 'comment']
        widgets = {
            'rating_type': forms.RadioSelect(),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience (optional)',
                'rows': 4
            }),
            'service': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.all()
        self.fields['service'].required = False
        self.fields['comment'].required = False