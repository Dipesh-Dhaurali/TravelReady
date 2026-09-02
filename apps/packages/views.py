from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import PredefinedPackage


def package_list(request):
    packages = PredefinedPackage.objects.filter(status='Active')

    destination = request.GET.get('destination')
    package_type = request.GET.get('type')
    filter_type = request.GET.get('filter')

    if filter_type == 'popular':
        packages = packages.filter(is_popular=True)
    if destination:
        packages = packages.filter(destination__slug=destination)
    if package_type:
        packages = packages.filter(package_type=package_type)

    from apps.destinations.models import Destination
    destination_list = Destination.objects.filter(status='Active')

    context = {
        'packages': packages,
        'selected_destination': destination,
        'selected_type': package_type,
        'destination_list': destination_list,
    }
    return render(request, 'packages/list.html', context)


def package_detail(request, slug):
    package = get_object_or_404(
        PredefinedPackage,
        slug=slug,
        status='Active'
    )
    related_activities = package.included_activities.all()

    context = {
        'package': package,
        'related_activities': related_activities,
    }
    return render(request, 'packages/detail.html', context)


def package_book_redirect(request, slug):
    package = get_object_or_404(
        PredefinedPackage,
        slug=slug,
        status='Active'
    )
    checkout_url = reverse('bookings:booking_checkout') + f'?package={package.slug}'
    return redirect(checkout_url)
