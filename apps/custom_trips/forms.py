from django import forms
from .models import CustomQuotationRequest


class CustomQuotationForm(forms.ModelForm):
    class Meta:
        model = CustomQuotationRequest
        exclude = [
            'user',
            'admin_quoted_price',
            'admin_notes',
            'generated_itinerary',
            'status',
            'created_at',
            'updated_at',
        ]
        widgets = {
            'desired_route': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe your desired route and locations...',
                }
            ),
            'adults': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 1,
                }
            ),
            'children': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                }
            ),
            'infants': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                }
            ),
            'budget': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                    'step': '0.01',
                    'placeholder': 'Optional',
                }
            ),
            'travel_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Special requirements, dietary needs, etc.',
                }
            ),
        }
