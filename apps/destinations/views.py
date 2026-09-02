from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import (
    Destination,
    Hotel,
    Activity,
    Transportation,
    Wishlist,
)

try:
    from apps.packages.models import PredefinedPackage
    HAS_PACKAGES = True
except ImportError:
    HAS_PACKAGES = False


def home(request):
    inside_country = Destination.objects.filter(
        destination_type='INSIDE_COUNTRY',
        status='Active',
    )[:6]
    outside_country = Destination.objects.filter(
        destination_type='OUTSIDE_COUNTRY',
        status='Active',
    )[:6]

    featured_packages = []
    if HAS_PACKAGES:
        featured_packages = PredefinedPackage.objects.filter(
            status='Active'
        ).select_related('destination').order_by('-is_popular', '-created_at')[:6]

    context = {
        'inside_country': inside_country,
        'inside_destinations': inside_country,
        'outside_country': outside_country,
        'outside_destinations': outside_country,
        'featured_packages': featured_packages,
        'packages': featured_packages,
    }
    return render(request, 'home.html', context)


def destination_list(request):
    destinations = Destination.objects.filter(status='Active')
    destination_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')

    if destination_type:
        destinations = destinations.filter(destination_type=destination_type)

    if search_query:
        destinations = destinations.filter(
            Q(name__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(district__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    context = {
        'destinations': destinations,
        'destination_type': destination_type,
        'search_query': search_query,
    }
    return render(request, 'destinations/list.html', context)


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug, status='Active')
    hotels = destination.hotels.all()
    activities = destination.activities.filter(is_available=True)
    transportations = destination.transportations.all()

    packages = []
    if HAS_PACKAGES:
        packages = PredefinedPackage.objects.filter(
            destination=destination,
            status='Active',
        )

    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            destination=destination,
        ).exists()

    context = {
        'destination': destination,
        'hotels': hotels,
        'activities': activities,
        'transportations': transportations,
        'packages': packages,
        'is_in_wishlist': is_in_wishlist,
    }
    return render(request, 'destinations/detail.html', context)


def calculate_price_htmx(request, slug):
    if request.method != 'POST':
        return HttpResponse(status=405)

    destination = get_object_or_404(Destination, slug=slug, status='Active')

    days = int(request.POST.get('days', 1) or 1)
    package_type = request.POST.get('package_type', 'STANDARD')
    adults = int(request.POST.get('adults', 1) or 1)
    children = int(request.POST.get('children', 0) or 0)
    hotel_category = request.POST.get('hotel_category', '')
    selected_activities = request.POST.getlist('activities[]')
    selected_transport = request.POST.getlist('transport[]')

    base_cost = destination.base_visit_cost * Decimal(days)

    package_multipliers = {
        'ECONOMY': Decimal('0.8'),
        'STANDARD': Decimal('1.0'),
        'PREMIUM': Decimal('1.3'),
        'LUXURY': Decimal('1.6'),
    }
    multiplier = package_multipliers.get(package_type, Decimal('1.0'))
    base_cost = base_cost * multiplier

    hotel_cost = Decimal('0')
    hotel = None
    if hotel_category:
        hotel = destination.hotels.filter(category=hotel_category).first()
        if hotel:
            hotel_cost = hotel.per_night_rate * Decimal(days - 1 if days > 1 else 1)

    activities_cost = Decimal('0')
    selected_activity_objs = []
    if selected_activities:
        activity_qs = destination.activities.filter(
            id__in=selected_activities,
            is_available=True,
        )
        for act in activity_qs:
            selected_activity_objs.append(act)
            activities_cost += (act.adult_price * Decimal(adults)) + (
                act.child_price * Decimal(children)
            )

    transport_cost = Decimal('0')
    selected_transport_objs = []
    if selected_transport:
        transport_qs = destination.transportations.filter(id__in=selected_transport)
        for trans in transport_qs:
            selected_transport_objs.append(trans)
            if trans.per_vehicle_price and trans.per_vehicle_price > 0:
                transport_cost += trans.per_vehicle_price
            else:
                transport_cost += trans.per_person_price * Decimal(
                    adults + children
                )

    total_people = adults + children
    per_person_base = base_cost / Decimal(total_people) if total_people > 0 else base_cost
    subtotal = base_cost + hotel_cost + activities_cost + transport_cost
    tax_rate = Decimal('0.13')
    tax = subtotal * tax_rate
    grand_total = subtotal + tax

    breakdown = {
        'destination': destination,
        'days': days,
        'package_type': package_type,
        'adults': adults,
        'children': children,
        'total_people': total_people,
        'base_cost': base_cost,
        'per_person_base': per_person_base,
        'hotel': hotel,
        'hotel_cost': hotel_cost,
        'activities': selected_activity_objs,
        'activities_cost': activities_cost,
        'transportations': selected_transport_objs,
        'transport_cost': transport_cost,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'multiplier': multiplier,
    }

    html = render_to_string(
        'destinations/partials/price_breakdown.html',
        breakdown,
        request=request,
    )
    return HttpResponse(html)


def search_destinations_htmx(request):
    search_query = request.GET.get('q', '')
    destination_type = request.GET.get('type', '')

    destinations = Destination.objects.filter(status='Active')

    if destination_type:
        destinations = destinations.filter(destination_type=destination_type)

    if search_query:
        destinations = destinations.filter(
            Q(name__icontains=search_query)
            | Q(location__icontains=search_query)
            | Q(district__icontains=search_query)
        )

    html = render_to_string(
        'destinations/partials/destination_cards.html',
        {'destinations': destinations},
        request=request,
    )
    return HttpResponse(html)


@login_required
def add_to_wishlist(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        destination=destination,
    )
    if created:
        messages.success(request, f'{destination.name} added to your wishlist.')
    else:
        messages.info(request, f'{destination.name} is already in your wishlist.')

    if request.headers.get('HX-Request'):
        html = render_to_string(
            'destinations/partials/wishlist_button.html',
            {
                'destination': destination,
                'is_in_wishlist': True,
            },
            request=request,
        )
        return HttpResponse(html)

    return redirect('destinations:destination_detail', slug=slug)


@login_required
def remove_from_wishlist(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    deleted, _ = Wishlist.objects.filter(
        user=request.user,
        destination=destination,
    ).delete()

    if deleted:
        messages.success(request, f'{destination.name} removed from your wishlist.')
    else:
        messages.info(request, f'{destination.name} was not in your wishlist.')

    if request.headers.get('HX-Request'):
        html = render_to_string(
            'destinations/partials/wishlist_button.html',
            {
                'destination': destination,
                'is_in_wishlist': False,
            },
            request=request,
        )
        return HttpResponse(html)

    return redirect('destinations:destination_detail', slug=slug)


def about_us(request):
    return render(request, 'pages/about.html')


def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            messages.success(request, f'Thank you {name}! Your message has been sent successfully. Our team will contact you at {email} within 24 hours.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('destinations_home:contact_us')
    return render(request, 'pages/contact.html')


def blog_list(request):
    return render(request, 'pages/blogs.html')


def faq_view(request):
    return render(request, 'pages/faq.html')


def terms_view(request):
    return render(request, 'pages/terms.html')


def privacy_view(request):
    return render(request, 'pages/privacy.html')

