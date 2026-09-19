from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse

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


PACKAGE_MULTIPLIERS = {
    'SINGLE': Decimal('1.0'),
    'COUPLE': Decimal('1.8'),
    'FAMILY': Decimal('2.5'),
}
SERVICE_CHARGE_RATE = Decimal('0.10')
VAT_RATE = Decimal('0.13')


def _parse_raw_int(value, default):
    if value is None or str(value).strip() == '':
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_positive_int(value, default, min_value=0):
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    if v < min_value:
        return default
    return v


def validate_destination_inputs(days, adults, children, package_type='SINGLE'):
    errors = []
    if days < 1:
        errors.append('Number of days must be at least 1.')
    if adults < 1:
        errors.append('There must be at least 1 adult.')
    if children < 0:
        errors.append('Number of children cannot be negative.')
    if package_type not in PACKAGE_MULTIPLIERS:
        errors.append('Invalid package type.')
    return errors


def calculate_destination_price(
    destination,
    days=3,
    package_type='SINGLE',
    adults=2,
    children=0,
    hotel_category='',
    selected_activities=None,
    selected_transport=None,
):
    selected_activities = selected_activities or []
    selected_transport = selected_transport or []

    multiplier = PACKAGE_MULTIPLIERS.get(package_type, Decimal('1.0'))

    base_price = destination.base_visit_cost * multiplier
    extra_days = days - 1 if days > 1 else 0
    extra_days_price = destination.base_visit_cost * Decimal(extra_days) * multiplier
    base_cost = base_price + extra_days_price

    hotel_total = Decimal('0')
    hotel = None
    if hotel_category:
        hotel = destination.hotels.filter(category=hotel_category).first()
        if hotel:
            hotel_nights = days - 1 if days > 1 else 1
            hotel_total = hotel.per_night_rate * Decimal(hotel_nights)

    activity_adult_per_unit = Decimal('0')
    activity_child_per_unit = Decimal('0')
    activities_total = Decimal('0')
    selected_activity_objs = []
    if selected_activities:
        activity_qs = destination.activities.filter(
            id__in=selected_activities,
            is_available=True,
        )
        for act in activity_qs:
            selected_activity_objs.append(act)
            activity_adult_per_unit += act.adult_price
            activity_child_per_unit += act.child_price
            activities_total += (act.adult_price * Decimal(adults)) + (
                act.child_price * Decimal(children)
            )

    transport_total = Decimal('0')
    selected_transport_objs = []
    if selected_transport:
        transport_qs = destination.transportations.filter(id__in=selected_transport)
        for trans in transport_qs:
            selected_transport_objs.append(trans)
            if trans.per_vehicle_price and trans.per_vehicle_price > 0:
                transport_total += trans.per_vehicle_price
            else:
                transport_total += trans.per_person_price * Decimal(adults + children)

    total_people = adults + children
    per_person_base = base_cost / Decimal(total_people) if total_people > 0 else base_cost
    subtotal = base_cost + hotel_total + activities_total + transport_total
    if subtotal < 0:
        subtotal = Decimal('0')
    service_charge = subtotal * SERVICE_CHARGE_RATE
    vat = (subtotal + service_charge) * VAT_RATE
    grand_total = subtotal + service_charge + vat
    if grand_total < 0:
        grand_total = Decimal('0')

    return {
        'destination': destination,
        'days': days,
        'package_type': package_type,
        'adults': adults,
        'children': children,
        'total_people': total_people,
        'base_price': base_price,
        'extra_days_price': extra_days_price,
        'base_cost': base_cost,
        'per_person_base': per_person_base,
        'hotel': hotel,
        'hotel_total': hotel_total,
        'activities': selected_activity_objs,
        'activity_adult_total': activity_adult_per_unit,
        'activity_child_total': activity_child_per_unit,
        'activities_total': activities_total,
        'transportations': selected_transport_objs,
        'transport_total': transport_total,
        'subtotal': subtotal,
        'service_charge': service_charge,
        'vat': vat,
        'grand_total': grand_total,
        'multiplier': multiplier,
    }


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

    default_days = 3
    default_package_type = 'SINGLE'
    default_adults = 2
    default_children = 0

    breakdown = calculate_destination_price(
        destination=destination,
        days=default_days,
        package_type=default_package_type,
        adults=default_adults,
        children=default_children,
    )

    context = {
        'destination': destination,
        'hotels': hotels,
        'activities': activities,
        'transportations': transportations,
        'packages': packages,
        'is_in_wishlist': is_in_wishlist,
        'validation_errors': [],
    }
    context.update(breakdown)
    return render(request, 'destinations/detail.html', context)


def calculate_price_htmx(request, slug):
    if request.method != 'POST':
        return HttpResponse(status=405)

    destination = get_object_or_404(Destination, slug=slug, status='Active')

    raw_days = _parse_raw_int(request.POST.get('num_days', 1), 1)
    package_type = request.POST.get('package_type', 'SINGLE')
    if package_type not in PACKAGE_MULTIPLIERS:
        package_type = 'SINGLE'
    raw_adults = _parse_raw_int(request.POST.get('adults', 1), 1)
    raw_children = _parse_raw_int(request.POST.get('children', 0), 0)
    hotel_category = request.POST.get('hotel_category', '')
    selected_activities = request.POST.getlist('activities')
    selected_transport = request.POST.getlist('transportation')

    validation_errors = validate_destination_inputs(raw_days, raw_adults, raw_children, package_type)

    days = max(1, raw_days)
    adults = max(1, raw_adults)
    children = max(0, raw_children)

    breakdown = calculate_destination_price(
        destination=destination,
        days=days,
        package_type=package_type,
        adults=adults,
        children=children,
        hotel_category=hotel_category,
        selected_activities=selected_activities,
        selected_transport=selected_transport,
    )

    if breakdown['grand_total'] <= Decimal('0'):
        validation_errors.append('Estimated total must be greater than 0.')

    breakdown['validation_errors'] = validation_errors
    breakdown['adults'] = adults
    breakdown['children'] = children
    breakdown['days'] = days

    html = render_to_string(
        'destinations/partials/price_breakdown.html',
        breakdown,
        request=request,
    )
    return HttpResponse(html)


@login_required
def book_destination_redirect(request, slug):
    destination = get_object_or_404(Destination, slug=slug, status='Active')

    if request.method == 'POST':
        raw_days = _parse_raw_int(request.POST.get('num_days', 1), 1)
        package_type = request.POST.get('package_type', 'SINGLE')
        if package_type not in PACKAGE_MULTIPLIERS:
            package_type = 'SINGLE'
        raw_adults = _parse_raw_int(request.POST.get('adults', 1), 1)
        raw_children = _parse_raw_int(request.POST.get('children', 0), 0)
        hotel_category = request.POST.get('hotel_category', '')
        selected_activities = request.POST.getlist('activities')
        selected_transport = request.POST.getlist('transportation')

        validation_errors = validate_destination_inputs(raw_days, raw_adults, raw_children, package_type)
        if validation_errors:
            for err in validation_errors:
                messages.error(request, err)
            return redirect('destinations:destination_detail', slug=slug)

        days = max(1, raw_days)
        adults = max(1, raw_adults)
        children = max(0, raw_children)

        breakdown = calculate_destination_price(
            destination=destination,
            days=days,
            package_type=package_type,
            adults=adults,
            children=children,
            hotel_category=hotel_category,
            selected_activities=selected_activities,
            selected_transport=selected_transport,
        )
        grand_total = breakdown['grand_total']

        if grand_total <= 0:
            messages.error(request, 'The estimated total must be greater than 0.')
            return redirect('destinations:destination_detail', slug=slug)

        from apps.custom_trips.models import CustomTrip, CustomTripDestination

        custom_trip = CustomTrip.objects.create(
            trip_name=f"{destination.name} - {package_type.title()} Package",
            user=request.user,
            total_days=days,
            package_type=package_type,
            selected_hotel_category=hotel_category,
            adults=adults,
            children=children,
            infants=0,
            total_calculated_price=grand_total,
            status='SAVED',
        )

        CustomTripDestination.objects.create(
            custom_trip=custom_trip,
            destination=destination,
            order=1,
            days_stay=days,
        )

        if selected_activities:
            custom_trip.selected_activities.set(selected_activities)
        if selected_transport:
            custom_trip.selected_transportation.set(selected_transport)

        custom_trip.save()

        checkout_url = reverse('bookings:booking_checkout') + f'?custom_trip={custom_trip.pk}'
        return redirect(checkout_url)

    return redirect('destinations:destination_detail', slug=slug)


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

