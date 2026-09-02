from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<str:booking_id>/', views.payment_page, name='payment_page'),
    path('ticket/<str:ticket_id>/', views.ticket_payment_page, name='ticket_payment_page'),
    path('<int:pk>/verify/', views.verify_payment, name='verify_payment'),
    path('<int:pk>/reject/', views.reject_payment, name='reject_payment'),
    path('success/<int:pk>/', views.payment_success, name='payment_success'),
]
