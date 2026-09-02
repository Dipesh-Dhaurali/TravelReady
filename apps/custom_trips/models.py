from django.db import models
from django.contrib.auth.models import User


class CustomTrip(models.Model):
    HOTEL_CATEGORY_CHOICES = [
        ('BUDGET', 'Budget'),
        ('THREE_STAR', '3 Star'),
        ('FOUR_STAR', '4 Star'),
        ('LUXURY', 'Luxury'),
    ]

    STATUS = [
        ('DRAFT', 'Draft'),
        ('SAVED', 'Saved'),
        ('CONVERTED', 'Converted to Booking'),
    ]

    trip_name = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_trips',
    )
    total_days = models.IntegerField(default=0)
    selected_hotel_category = models.CharField(
        max_length=15,
        choices=HOTEL_CATEGORY_CHOICES,
        default='BUDGET',
    )
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    infants = models.IntegerField(default=0)
    selected_activities = models.ManyToManyField(
        'destinations.Activity',
        blank=True,
    )
    selected_transportation = models.ManyToManyField(
        'destinations.Transportation',
        blank=True,
    )
    total_calculated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    is_booked = models.BooleanField(default=False)
    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default='DRAFT',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trip_name} ({self.user.username})"


class CustomTripDestination(models.Model):
    custom_trip = models.ForeignKey(
        CustomTrip,
        on_delete=models.CASCADE,
        related_name='trip_destinations',
    )
    destination = models.ForeignKey(
        'destinations.Destination',
        on_delete=models.CASCADE,
    )
    order = models.IntegerField(default=1)
    days_stay = models.IntegerField(default=2)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.custom_trip.trip_name}: {self.destination.name} ({self.days_stay}d)"


class CustomQuotationRequest(models.Model):
    STATUS = [
        ('PENDING', 'Pending Review'),
        ('QUOTED', 'Quoted'),
        ('ACCEPTED', 'Accepted by User'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quotation_requests',
    )
    desired_route = models.TextField(
        help_text='Describe your desired route/locations',
    )
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    infants = models.IntegerField(default=0)
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    travel_date = models.DateField(blank=True, null=True)
    notes = models.TextField(
        blank=True,
        help_text='Special requirements, dietary needs, etc.',
    )
    admin_quoted_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
    )
    admin_notes = models.TextField(blank=True)
    generated_itinerary = models.TextField(
        blank=True,
        help_text='Admin generated day-by-day itinerary',
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default='PENDING',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quote #{self.id}: {self.user.username} - {self.status}"
