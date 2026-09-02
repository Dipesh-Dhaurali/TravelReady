from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'travel_date',
            'return_date',
            'adults',
            'children',
            'infants',
            'special_requirements',
            'emergency_contact_name',
            'emergency_contact_phone',
            'traveler_names',
            'payment_option',
        ]
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
        }
