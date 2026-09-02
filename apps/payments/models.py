from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Payment(models.Model):
    PAYMENT_OPTION = [
        ('FULL', 'Full Payment'),
        ('PARTIAL_30', '30% Partial'),
    ]

    PAYMENT_METHOD = [
        ('ESEWA', 'eSewa'),
        ('KHALTI', 'Khalti'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]

    VERIFICATION_STATUS = [
        ('PENDING', 'Pending Verification'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    payment_ref = models.CharField(max_length=30, unique=True, editable=False)
    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.SET_NULL,
        related_name='payments',
        blank=True,
        null=True,
    )
    ticket = models.ForeignKey(
        'tickets.StandaloneTicket',
        on_delete=models.SET_NULL,
        related_name='payments',
        blank=True,
        null=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_option = models.CharField(
        max_length=15, choices=PAYMENT_OPTION, default='FULL'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD, default='BANK_TRANSFER'
    )
    transaction_ref = models.CharField(
        max_length=100,
        blank=True,
        help_text='Gateway/Reference ID from payment',
    )
    payment_receipt = models.ImageField(
        upload_to='payments/receipts/',
        blank=True,
        null=True,
        help_text='Upload scanned deposit voucher or screenshot',
    )
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    depositor_name = models.CharField(max_length=100, blank=True)
    deposit_date = models.DateField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=15, choices=VERIFICATION_STATUS, default='PENDING'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='verified_payments',
        blank=True,
        null=True,
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    admin_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_ref:
            temp_id = self.pk
            super().save(*args, **kwargs)
            if temp_id is None:
                temp_id = self.pk
            date_str = timezone.now().strftime('%Y%m%d')
            self.payment_ref = f'PAY-{date_str}-{temp_id:05d}'
            kwargs['force_update'] = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.payment_ref} - {self.amount} ({self.get_verification_status_display()})'
