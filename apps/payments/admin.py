from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_ref',
        'user',
        'amount',
        'payment_method',
        'verification_status',
        'created_at',
    )
    list_filter = ('verification_status', 'payment_method', 'payment_option')
    search_fields = ('payment_ref', 'transaction_ref', 'user__username')
