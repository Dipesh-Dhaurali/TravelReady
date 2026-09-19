from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('', views.destination_list, name='destination_list'),
    path('all/', views.destination_list, name='list'),
    path('<slug:slug>/', views.destination_detail, name='destination_detail'),
    path(
        '<slug:slug>/calculate-price/',
        views.calculate_price_htmx,
        name='calculate_price_htmx',
    ),
    path(
        '<slug:slug>/book/',
        views.book_destination_redirect,
        name='book_destination',
    ),
    path(
        '<slug:slug>/wishlist/add/',
        views.add_to_wishlist,
        name='add_to_wishlist',
    ),
    path(
        '<slug:slug>/wishlist/remove/',
        views.remove_from_wishlist,
        name='remove_from_wishlist',
    ),
    path(
        'search/',
        views.search_destinations_htmx,
        name='search_destinations_htmx',
    ),
]
