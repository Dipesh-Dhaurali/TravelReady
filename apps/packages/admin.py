from django.contrib import admin
from .models import PredefinedPackage


@admin.register(PredefinedPackage)
class PackageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = (
        'title',
        'destination',
        'package_type',
        'base_days',
        'base_price',
        'is_popular',
        'status',
    )
    filter_horizontal = ('included_activities',)
