from django.contrib import admin
from .models import (
    CustomTrip,
    CustomTripDestination,
    CustomQuotationRequest,
)


class CustomTripDestinationInline(admin.TabularInline):
    model = CustomTripDestination
    extra = 1


class CustomTripAdmin(admin.ModelAdmin):
    inlines = [CustomTripDestinationInline]
    filter_horizontal = (
        'selected_activities',
        'selected_transportation',
    )


class CustomQuotationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'status',
        'admin_quoted_price',
        'created_at',
    )
    list_filter = ('status',)


admin.site.register(CustomTrip, CustomTripAdmin)
admin.site.register(CustomTripDestination)
admin.site.register(CustomQuotationRequest, CustomQuotationRequestAdmin)
