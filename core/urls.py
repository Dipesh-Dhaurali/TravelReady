from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('destinations/', include('apps.destinations.urls')),
    path('packages/', include('apps.packages.urls')),
    path('builder/', include('apps.custom_trips.urls')),
    path('booking/', include('apps.bookings.urls')),
    path('tickets/', include('apps.tickets.urls')),
    path('payments/', include('apps.payments.urls')),
    path('dashboard/', include('apps.accounts.urls_dashboard')),
    path('', include('apps.destinations.urls_home')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
