from django import forms
from .models import PredefinedPackage


class PackageForm(forms.ModelForm):
    class Meta:
        model = PredefinedPackage
        exclude = ['slug', 'created_at', 'updated_at']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Pokhara Adventure 4 Days'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'package_type': forms.Select(attrs={'class': 'form-select'}),
            'base_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'per_day_extra_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'included_activities': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'hotel': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Package overview...'}),
            'highlights': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comma separated highlights...'}),
            'inclusions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What is included...'}),
            'exclusions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What is excluded...'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_popular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
