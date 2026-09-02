from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Booking(models.Model):
    STATUS = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('TRIP_STARTED', 'Trip Started'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_OPTIONS = [
        ('FULL', 'Full Payment'),
        ('PARTIAL_30', '30% Advance'),
    ]

    STATUS_ORDER = {
        'PENDING': 0,
        'CONFIRMED': 1,
        'TRIP_STARTED': 2,
        'COMPLETED': 3,
        'CANCELLED': -1,
    }

    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(
        'packages.PredefinedPackage',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='bookings',
    )
    custom_trip = models.ForeignKey(
        'custom_trips.CustomTrip',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='bookings',
    )
    travel_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    infants = models.IntegerField(default=0)
    special_requirements = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    traveler_names = models.TextField(blank=True, help_text='Comma separated list')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='PENDING')
    payment_option = models.CharField(max_length=15, choices=PAYMENT_OPTIONS, default='FULL')
    payment_verified = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.booking_id}"

    def save(self, *args, **kwargs):
        if not self.booking_id:
            year = datetime.now().year
            super().save(*args, **kwargs)
            self.booking_id = f"TRV-{year}-{self.pk:05d}"
            kwargs['force_update'] = True
        super().save(*args, **kwargs)

    def get_progress_percentage(self):
        progress_map = {
            'PENDING': 0,
            'CONFIRMED': 40,
            'TRIP_STARTED': 70,
            'COMPLETED': 100,
            'CANCELLED': 0,
        }
        return progress_map.get(self.status, 0)

    def get_progress_steps(self):
        current_order = self.STATUS_ORDER.get(self.status, -1)
        return [
            {
                'name': 'Request Received',
                'done': True,
            },
            {
                'name': 'Payment Verified',
                'done': current_order >= self.STATUS_ORDER['CONFIRMED'],
            },
            {
                'name': 'Hotel/Transport Confirmed',
                'done': current_order >= self.STATUS_ORDER['CONFIRMED'],
            },
            {
                'name': 'Itinerary Ready',
                'done': current_order >= self.STATUS_ORDER['TRIP_STARTED'],
            },
            {
                'name': 'Trip Completed',
                'done': self.status == 'COMPLETED',
            },
        ]

    def generate_itinerary_text(self):
        lines = []
        lines.append(f"BOOKING ITINERARY - {self.booking_id}")
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"Booking Status: {self.get_status_display()}")
        lines.append(f"Travel Date: {self.travel_date}")
        if self.return_date:
            lines.append(f"Return Date: {self.return_date}")
        lines.append("")
        lines.append(f"Travelers: {self.adults} Adults, {self.children} Children, {self.infants} Infants")
        if self.traveler_names:
            lines.append(f"Traveler Names: {self.traveler_names}")
        lines.append("")
        lines.append(f"Emergency Contact: {self.emergency_contact_name} - {self.emergency_contact_phone}")
        if self.special_requirements:
            lines.append(f"Special Requirements: {self.special_requirements}")
        lines.append("")
        lines.append("-" * 50)

        trip_source = self.package or self.custom_trip
        if trip_source:
            trip_name = getattr(trip_source, 'name', getattr(trip_source, 'title', 'Trip'))
            lines.append(f"Trip: {trip_name}")
            lines.append("")

            days = getattr(trip_source, 'days', None)
            if days:
                if hasattr(days, 'all'):
                    for day in days.all():
                        day_num = getattr(day, 'day_number', '')
                        day_title = getattr(day, 'title', getattr(day, 'name', ''))
                        day_desc = getattr(day, 'description', '')
                        lines.append(f"--- Day {day_num}: {day_title} ---")
                        if day_desc:
                            lines.append(day_desc)
                        lines.append("")
                else:
                    lines.append(str(days))
            else:
                duration = getattr(trip_source, 'duration_days', getattr(trip_source, 'no_of_days', None))
                if duration:
                    for day_num in range(1, int(duration) + 1):
                        lines.append(f"--- Day {day_num} ---")
                        lines.append(f"Day {day_num} of your {trip_name} adventure.")
                        lines.append("")
        else:
            lines.append("--- Day 1: Arrival ---")
            lines.append("Welcome! Arrival at your destination and check-in.")
            lines.append("")

        lines.append("-" * 50)
        lines.append(f"Total Cost: Rs. {self.total_cost}")
        lines.append(f"Amount Paid: Rs. {self.amount_paid}")
        lines.append("")
        lines.append("Thank you for booking with us!")

        return "\n".join(lines)
