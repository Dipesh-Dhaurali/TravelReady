from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Destination(models.Model):
    DESTINATION_TYPE = [
        ('INSIDE_COUNTRY', 'Inside Country'),
        ('OUTSIDE_COUNTRY', 'Outside Country'),
    ]
    STATUS = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    destination_type = models.CharField(
        max_length=20,
        choices=DESTINATION_TYPE,
        default='INSIDE_COUNTRY',
    )
    location = models.CharField(max_length=200, blank=True)
    district = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    main_image = models.ImageField(
        upload_to='destinations/main/',
        blank=True,
        null=True,
    )
    rules_regulations = models.TextField(blank=True)
    best_season = models.CharField(max_length=200, blank=True)
    base_visit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default='Active',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DestinationGallery(models.Model):
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='gallery',
    )
    image = models.ImageField(upload_to='destinations/gallery/')
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.destination.name} Gallery"


class Hotel(models.Model):
    CATEGORY_CHOICES = [
        ('BUDGET', 'Budget'),
        ('THREE_STAR', '3 Star'),
        ('FOUR_STAR', '4 Star'),
        ('LUXURY', 'Luxury'),
    ]

    name = models.CharField(max_length=200)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='hotels',
    )
    category = models.CharField(
        max_length=15,
        choices=CATEGORY_CHOICES,
        default='BUDGET',
    )
    per_night_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    room_types = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comma separated: Single,Double,Deluxe',
    )
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Activity(models.Model):
    title = models.CharField(max_length=200)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='activities',
    )
    adult_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    child_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1,
    )
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='activities/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Transportation(models.Model):
    VEHICLE_CHOICES = [
        ('BUS', 'Tourist Bus'),
        ('CAR', 'Private Car'),
        ('JEEP', 'Jeep'),
        ('FLIGHT', 'Flight'),
    ]

    route_origin = models.CharField(max_length=200)
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='transportations',
    )
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES)
    per_person_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    per_vehicle_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=2,
    )

    def __str__(self):
        return f"{self.route_origin} -> {self.destination.name} ({self.get_vehicle_type_display()})"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist',
    )
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'destination')
