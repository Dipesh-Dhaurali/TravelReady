from django.urls import path
from . import views

app_name = 'custom_trips'

urlpatterns = [
    path('', views.trip_builder, name='trip_builder'),
    path('builder/', views.trip_builder, name='builder'),
    path('calculate/', views.calculate_trip_htmx, name='calculate_trip_htmx'),
    path('save/', views.save_custom_trip, name='save_custom_trip'),
    path('mine/', views.my_custom_trips, name='my_custom_trips'),
    path('mine/all/', views.my_custom_trips, name='my_trips'),
    path('<int:pk>/', views.custom_trip_detail, name='custom_trip_detail'),
    path('<int:pk>/book/', views.book_custom_trip, name='book_custom_trip'),
    path('quotation/request/', views.quotation_request, name='quotation_request'),
    path('quotation/<int:pk>/', views.quotation_detail, name='quotation_detail'),
    path(
        'quotation/<int:pk>/accept/',
        views.quotation_accept,
        name='quotation_accept',
    ),
]
