from django import forms
from .models import StandaloneTicket


class TicketSearchForm(forms.Form):
    ticket_type = forms.ChoiceField(
        choices=[('', 'All'), ('BUS', 'Bus'), ('FLIGHT', 'Flight')],
        required=False
    )
    origin = forms.CharField(max_length=150, required=False)
    destination = forms.CharField(max_length=150, required=False)
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    passenger_count = forms.IntegerField(initial=1, min_value=1)


class TicketBookingForm(forms.ModelForm):
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = StandaloneTicket
        fields = ('passenger_count', 'passenger_names', 'travel_date')
        widgets = {
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
        }
