from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('all/', views.package_list, name='list'),
    path('<slug:slug>/', views.package_detail, name='package_detail'),
    path('<slug:slug>/book/', views.package_book_redirect, name='package_book'),
]
