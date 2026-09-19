from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today().isoformat()
        self.fields['travel_date'].widget.attrs.update({'min': today})
        self.fields['adults'].widget.attrs.update({'min': '1', 'max': '50'})
        self.fields['children'].widget.attrs.update({'min': '0', 'max': '50'})
        self.fields['infants'].widget.attrs.update({'min': '0', 'max': '50'})

    def clean_travel_date(self):
        travel_date = self.cleaned_data.get('travel_date')
        if not travel_date:
            raise ValidationError(_('Travel date is required.'))
        if travel_date < date.today():
            raise ValidationError(_('Travel date cannot be before today.'))
        return travel_date

    def clean_return_date(self):
        return_date = self.cleaned_data.get('return_date')
        travel_date = self.cleaned_data.get('travel_date')
        if return_date and travel_date and return_date < travel_date:
            raise ValidationError(_('Return date cannot be before travel date.'))
        return return_date

    def clean_adults(self):
        adults = self.cleaned_data.get('adults')
        if adults is None:
            raise ValidationError(_('Number of adults is required.'))
        if adults < 1:
            raise ValidationError(_('There must be at least 1 adult.'))
        if adults < 0:
            raise ValidationError(_('Number of adults cannot be negative.'))
        return adults

    def clean_children(self):
        children = self.cleaned_data.get('children')
        if children is None:
            raise ValidationError(_('Number of children is required.'))
        if children < 0:
            raise ValidationError(_('Number of children cannot be negative.'))
        return children

    def clean_infants(self):
        infants = self.cleaned_data.get('infants')
        if infants is None:
            raise ValidationError(_('Number of infants is required.'))
        if infants < 0:
            raise ValidationError(_('Number of infants cannot be negative.'))
        return infants

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone')
        if phone:
            digits = ''.join(c for c in phone if c.isdigit())
            if len(digits) != 10:
                raise ValidationError(_('Contact number must be exactly 10 digits.'))
        return phone

    def clean(self):
        cleaned_data = super().clean()
        travel_date = cleaned_data.get('travel_date')
        return_date = cleaned_data.get('return_date')
        adults = cleaned_data.get('adults')
        children = cleaned_data.get('children')
        infants = cleaned_data.get('infants')

        if travel_date and travel_date < date.today():
            self.add_error('travel_date', _('Travel date cannot be before today.'))

        if travel_date and return_date and return_date < travel_date:
            self.add_error('return_date', _('Return date cannot be before travel date.'))

        if adults is not None and adults < 1:
            self.add_error('adults', _('There must be at least 1 adult.'))

        if children is not None and children < 0:
            self.add_error('children', _('Number of children cannot be negative.'))

        if infants is not None and infants < 0:
            self.add_error('infants', _('Number of infants cannot be negative.'))

        total_people = (adults or 0) + (children or 0) + (infants or 0)
        if total_people < 1:
            self.add_error('adults', _('There must be at least 1 traveler.'))

        return cleaned_data
