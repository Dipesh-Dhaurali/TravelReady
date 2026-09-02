from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('checkout/', views.booking_checkout, name='booking_checkout'),
    path('checkout/', views.booking_checkout, name='checkout'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/itinerary/', views.download_itinerary, name='download_itinerary'),
    path('success/<int:pk>/', views.booking_success, name='booking_success'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
]
