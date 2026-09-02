from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


TICKET_TYPE = [
    ('BUS', 'Bus'),
    ('FLIGHT', 'Flight'),
]

STATUS = [
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELLED', 'Cancelled'),
]


class StandaloneTicket(models.Model):
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tickets', blank=True, null=True)
    ticket_type = models.CharField(choices=TICKET_TYPE, max_length=10, default='BUS')
    operator_name = models.CharField(max_length=100, blank=True)
    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)
    travel_date = models.DateField()
    travel_time = models.TimeField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    passenger_count = models.IntegerField(default=1)
    passenger_names = models.TextField(blank=True)
    seat_numbers = models.CharField(max_length=100, blank=True)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(choices=STATUS, default='PENDING', max_length=15)
    ticket_document = models.FileField(
        upload_to='tickets/documents/',
        blank=True,
        null=True,
        help_text='PDF ticket file'
    )
    payment_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            super().save(*args, **kwargs)
            year = timezone.now().year
            self.ticket_number = f'TKT-{year}-{self.pk:05d}'
            kwargs['force_update'] = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number}: {self.origin} -> {self.destination}"


class TicketSchedule(models.Model):
    ticket_type = models.CharField(choices=TICKET_TYPE, max_length=10)
    operator_name = models.CharField(max_length=100)
    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)
    departure_time = models.TimeField()
    arrival_time = models.TimeField(blank=True, null=True)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_seats = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    days_of_week = models.CharField(
        max_length=50,
        default='Mon,Tue,Wed,Thu,Fri,Sat,Sun',
        help_text='Comma separated days: Mon,Tue,Wed,Thu,Fri,Sat,Sun'
    )

    def __str__(self):
        return f"{self.ticket_type}: {self.origin} -> {self.destination} ({self.departure_time})"
