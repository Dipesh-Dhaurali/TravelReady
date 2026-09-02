from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('all/', views.ticket_list, name='list'),
    path('search/', views.ticket_search, name='ticket_search'),
    path('search/all/', views.ticket_search, name='search'),
    path('schedule/<int:schedule_id>/book/', views.ticket_book, name='ticket_book'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('<int:pk>/download/', views.download_ticket, name='download_ticket'),
]
