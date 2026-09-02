from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class PredefinedPackage(models.Model):
    PACKAGE_TYPE = [
        ('SINGLE', 'Single Person'),
        ('COUPLE', 'Couple'),
        ('FAMILY', 'Family'),
    ]

    STATUS = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    destination = models.ForeignKey(
        'destinations.Destination',
        on_delete=models.CASCADE,
        related_name='packages'
    )
    package_type = models.CharField(
        max_length=10,
        choices=PACKAGE_TYPE,
        default='SINGLE'
    )
    base_days = models.IntegerField(default=3)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    per_day_extra_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    included_activities = models.ManyToManyField(
        'destinations.Activity',
        blank=True,
        related_name='packages'
    )
    hotel = models.ForeignKey(
        'destinations.Hotel',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='packages'
    )
    description = models.TextField(blank=True)
    highlights = models.TextField(
        blank=True,
        help_text='Comma separated highlights'
    )
    inclusions = models.TextField(
        blank=True,
        help_text='What is included'
    )
    exclusions = models.TextField(
        blank=True,
        help_text='What is excluded'
    )
    thumbnail = models.ImageField(
        upload_to='packages/',
        blank=True,
        null=True
    )
    is_popular = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_package_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('packages:package_detail', kwargs={'slug': self.slug})
