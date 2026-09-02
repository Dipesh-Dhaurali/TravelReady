from django.contrib import admin
from .models import (
    Destination,
    DestinationGallery,
    Hotel,
    Activity,
    Transportation,
    Wishlist,
)


class DestinationGalleryInline(admin.TabularInline):
    model = DestinationGallery
    extra = 1


class HotelInline(admin.TabularInline):
    model = Hotel
    extra = 1


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 1


class TransportationInline(admin.TabularInline):
    model = Transportation
    extra = 1


class DestinationAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        DestinationGalleryInline,
        HotelInline,
        ActivityInline,
        TransportationInline,
    ]


admin.site.register(Destination, DestinationAdmin)
admin.site.register(DestinationGallery)
admin.site.register(Hotel)
admin.site.register(Activity)
admin.site.register(Transportation)
admin.site.register(Wishlist)
