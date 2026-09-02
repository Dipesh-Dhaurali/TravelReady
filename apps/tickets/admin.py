from django.contrib import admin
from .models import StandaloneTicket, TicketSchedule


class StandaloneTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'ticket_type', 'user', 'origin', 'destination', 'travel_date', 'total_price', 'status')


class TicketScheduleAdmin(admin.ModelAdmin):
    list_display = ('ticket_type', 'operator_name', 'origin', 'destination', 'departure_time', 'price_per_person', 'available_seats', 'is_active')


admin.site.register(StandaloneTicket, StandaloneTicketAdmin)
admin.site.register(TicketSchedule, TicketScheduleAdmin)
