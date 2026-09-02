from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            'payment_option',
            'payment_method',
            'transaction_ref',
            'payment_receipt',
            'bank_name',
            'bank_account_number',
            'depositor_name',
            'deposit_date',
        )
        widgets = {
            'deposit_date': forms.DateInput(attrs={'type': 'date'}),
        }
