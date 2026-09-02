from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-trips/', views.my_trips, name='my_trips'),
    path('quotations/', views.my_quotations, name='my_quotations'),
    path('tickets/', views.my_tickets, name='my_tickets'),
    path('itineraries/', views.my_itineraries, name='my_itineraries'),
    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('admin/destinations/', views.admin_destinations, name='admin_destinations'),
    path('admin/destinations/create/', views.admin_destination_create, name='admin_destination_create'),
    path('admin/destinations/<int:pk>/edit/', views.admin_destination_edit, name='admin_destination_edit'),
    path('admin/destinations/<int:pk>/delete/', views.admin_destination_delete, name='admin_destination_delete'),
    path('admin/bookings/', views.admin_bookings_list, name='admin_bookings'),
    path('admin/bookings/<int:pk>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('admin/quotations/', views.admin_quotations, name='admin_quotations'),
    path('admin/quotations/<int:pk>/', views.admin_quotation_detail, name='admin_quotation_detail'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/payments/<int:pk>/verify/', views.admin_payment_verify, name='admin_payment_verify'),
    path('admin/packages/', views.admin_packages, name='admin_packages'),
    path('admin/packages/create/', views.admin_package_create, name='admin_package_create'),
    path('admin/packages/<int:pk>/edit/', views.admin_package_edit, name='admin_package_edit'),
    path('admin/packages/<int:pk>/delete/', views.admin_package_delete, name='admin_package_delete'),
    path('admin/hotels/', views.admin_hotels, name='admin_hotels'),
    path('admin/hotels/create/', views.admin_hotel_create, name='admin_hotel_create'),
    path('admin/hotels/<int:pk>/edit/', views.admin_hotel_edit, name='admin_hotel_edit'),
    path('admin/hotels/<int:pk>/delete/', views.admin_hotel_delete, name='admin_hotel_delete'),
]
