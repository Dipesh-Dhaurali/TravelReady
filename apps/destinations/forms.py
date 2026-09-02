from django import forms
from .models import Destination, Hotel, Activity, Transportation


class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        exclude = ('slug', 'created_at', 'updated_at')


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grand Palace Hotel'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'per_night_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'room_types': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Single,Double,Deluxe'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Hotel description and amenities...'}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'


class TransportationForm(forms.ModelForm):
    class Meta:
        model = Transportation
        fields = '__all__'
