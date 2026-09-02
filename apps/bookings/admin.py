from django.contrib import admin
from .models import Booking


class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'status', 'total_cost', 'payment_verified', 'travel_date')
    list_filter = ('status', 'payment_verified', 'travel_date')
    search_fields = ('booking_id', 'user__username')


admin.site.register(Booking, BookingAdmin)
