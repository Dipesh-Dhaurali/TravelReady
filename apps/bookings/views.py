from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db import models
from .models import Booking
from .forms import BookingForm

from decimal import Decimal

from apps.destinations.views import (
    PACKAGE_MULTIPLIERS,
    SERVICE_CHARGE_RATE,
    VAT_RATE,
    _parse_raw_int,
    _safe_positive_int,
    validate_destination_inputs,
)


def _calculate_custom_trip_price(custom_trip, days=None, adults=None, children=None):
    from apps.destinations.models import Destination

    trip_destinations = custom_trip.trip_destinations.select_related('destination').all()
    days = days if days is not None else (custom_trip.total_days or 1)
    adults = adults if adults is not None else (custom_trip.adults or 1)
    children = children if children is not None else (custom_trip.children or 0)

    multiplier = PACKAGE_MULTIPLIERS.get(custom_trip.package_type, Decimal('1.0'))

    base_price_total = Decimal('0')
    extra_days_price_total = Decimal('0')
    num_dest = len(trip_destinations)
    for td in trip_destinations:
        dest = td.destination
        dest_days = days if num_dest <= 1 else (td.days_stay or max(1, days // num_dest))
        extra_days = dest_days - 1 if dest_days > 1 else 0
        base_price_total += dest.base_visit_cost * multiplier
        extra_days_price_total += dest.base_visit_cost * Decimal(extra_days) * multiplier
    if not trip_destinations:
        base_price_total = Decimal('0')
        extra_days_price_total = Decimal('0')

    base_cost = base_price_total + extra_days_price_total

    activities_total = Decimal('0')
    activity_adult_total_per = Decimal('0')
    activity_child_total_per = Decimal('0')
    for act in custom_trip.selected_activities.all():
        activity_adult_total_per += act.adult_price
        activity_child_total_per += act.child_price
        activities_total += (act.adult_price * Decimal(adults)) + (act.child_price * Decimal(children))

    transport_total = Decimal('0')
    for trans in custom_trip.selected_transportation.all():
        if trans.per_vehicle_price and trans.per_vehicle_price > 0:
            transport_total += trans.per_vehicle_price
        else:
            transport_total += trans.per_person_price * Decimal(adults + children)

    hotel_total = Decimal('0')
    valid_hotel_categories = [c[0] for c in custom_trip.HOTEL_CATEGORY_CHOICES]
    if (custom_trip.selected_hotel_category
            and custom_trip.selected_hotel_category in valid_hotel_categories
            and trip_destinations):
        cat = custom_trip.selected_hotel_category
        for td in trip_destinations:
            hotel = td.destination.hotels.filter(category=cat).first()
            if hotel:
                stay = days if num_dest <= 1 else (td.days_stay or max(1, days // num_dest))
                hotel_nights = stay - 1 if stay > 1 else 1
                hotel_total += hotel.per_night_rate * Decimal(hotel_nights)

    subtotal = base_cost + hotel_total + activities_total + transport_total
    if subtotal < 0:
        subtotal = Decimal('0')
    service_charge = subtotal * SERVICE_CHARGE_RATE
    vat = (subtotal + service_charge) * VAT_RATE
    grand_total = subtotal + service_charge + vat
    if grand_total < 0:
        grand_total = Decimal('0')

    return {
        'days': days,
        'adults': adults,
        'children': children,
        'base_price': base_price_total,
        'extra_days_price': extra_days_price_total,
        'activity_adult_total': activity_adult_total_per,
        'activity_child_total': activity_child_total_per,
        'activities_total': activities_total,
        'transport_total': transport_total,
        'hotel_total': hotel_total,
        'subtotal': subtotal,
        'service_charge': service_charge,
        'vat': vat,
        'grand_total': grand_total,
    }


@login_required
def booking_checkout(request):
    package_param = request.GET.get('package') or request.GET.get('package_id') or request.POST.get('package') or request.POST.get('package_id')
    trip_param = request.GET.get('custom_trip') or request.GET.get('custom_trip_id') or request.GET.get('trip') or request.POST.get('custom_trip') or request.POST.get('custom_trip_id') or request.POST.get('trip')
    quotation_param = request.GET.get('quotation') or request.GET.get('quotation_id') or request.POST.get('quotation') or request.POST.get('quotation_id')

    package = None
    custom_trip = None
    quotation = None

    if package_param:
        from apps.packages.models import PredefinedPackage
        if str(package_param).isdigit():
            package = PredefinedPackage.objects.filter(id=package_param).first()
        else:
            package = PredefinedPackage.objects.filter(slug=package_param).first()

    if not package and trip_param:
        from apps.custom_trips.models import CustomTrip
        custom_trip = CustomTrip.objects.filter(id=trip_param).first()

    if not package and not custom_trip and quotation_param:
        from apps.custom_trips.models import CustomQuotationRequest
        quotation = CustomQuotationRequest.objects.filter(id=quotation_param).first()

    initial = {}
    if package:
        initial['adults'] = 1
        initial['children'] = 0
        initial['infants'] = 0
        if package.base_days:
            from datetime import date, timedelta
            initial['travel_date'] = date.today() + timedelta(days=7)
            initial['return_date'] = initial['travel_date'] + timedelta(days=package.base_days)
    if custom_trip:
        initial['adults'] = custom_trip.adults or 1
        initial['children'] = custom_trip.children or 0
        initial['infants'] = custom_trip.infants or 0
        if custom_trip.total_days:
            from datetime import date, timedelta
            initial['travel_date'] = date.today() + timedelta(days=7)
            initial['return_date'] = initial['travel_date'] + timedelta(days=custom_trip.total_days)

    price_context = {}
    if custom_trip:
        breakdown = _calculate_custom_trip_price(custom_trip)
        grand_total_display = breakdown['grand_total']
        if custom_trip.total_calculated_price and custom_trip.total_calculated_price > 0:
            stored = Decimal(str(custom_trip.total_calculated_price))
            if abs(stored - grand_total_display) > 1:
                grand_total_display = stored
        partial_amount = grand_total_display * Decimal('0.30')
        balance_amount = grand_total_display - partial_amount

        price_context = {
            'is_custom_trip': True,
            'base_price': breakdown['base_price'],
            'extra_days_price': breakdown['extra_days_price'],
            'activity_adult_total': breakdown['activity_adult_total'],
            'activity_child_total': breakdown['activity_child_total'],
            'activities_total': breakdown['activities_total'],
            'transport_total': breakdown['transport_total'],
            'hotel_total': breakdown['hotel_total'],
            'subtotal': breakdown['subtotal'],
            'service_charge': breakdown['service_charge'],
            'vat': breakdown['vat'],
            'grand_total': grand_total_display,
            'partial_amount': partial_amount,
            'balance_amount': balance_amount,
            'validation_errors': [],
        }
    elif package:
        price_context = {
            'is_custom_trip': False,
            'validation_errors': [],
        }
    elif quotation:
        price_context = {
            'is_custom_trip': False,
            'grand_total': Decimal(str(quotation.admin_quoted_price or quotation.budget or 0)),
            'validation_errors': [],
        }

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            if package:
                booking.package = package
            if custom_trip:
                booking.custom_trip = custom_trip

            base_cost = Decimal('0')
            if package:
                base_cost = Decimal(str(package.base_price))
            elif custom_trip:
                adults_val = max(1, int(form.cleaned_data.get('adults') or 1))
                children_val = max(0, int(form.cleaned_data.get('children') or 0))
                infants_val = max(0, int(form.cleaned_data.get('infants') or 0))
                raw_days = _parse_raw_int(request.POST.get('total_days', custom_trip.total_days or 1), 1)
                days_val = max(1, raw_days)
                recalc = _calculate_custom_trip_price(
                    custom_trip,
                    days=days_val,
                    adults=adults_val,
                    children=children_val,
                )
                base_cost = recalc['grand_total']
                custom_trip.adults = adults_val
                custom_trip.children = children_val
                custom_trip.infants = infants_val
                custom_trip.total_days = days_val
                custom_trip.total_calculated_price = base_cost
                custom_trip.save()
                td_list = list(custom_trip.trip_destinations.all())
                if len(td_list) == 1:
                    td_list[0].days_stay = days_val
                    td_list[0].save()
            elif quotation:
                q_price = quotation.admin_quoted_price or quotation.budget or 0
                base_cost = Decimal(str(q_price))

            if custom_trip or quotation:
                total_cost = base_cost
            else:
                adults = Decimal(str(booking.adults or 1))
                children = Decimal(str(booking.children or 0))
                infants = Decimal(str(booking.infants or 0))

                per_person = base_cost if base_cost > Decimal('0') else Decimal('0')
                child_factor = Decimal('0.5')
                infant_factor = Decimal('0.1')

                total_cost = (adults * per_person) + (children * per_person * child_factor) + (infants * per_person * infant_factor)
                if total_cost == Decimal('0') and base_cost > Decimal('0'):
                    total_cost = base_cost

            if total_cost <= Decimal('0'):
                messages.error(request, 'Total booking amount must be greater than 0. Please review your selections.')
            else:
                booking.total_cost = round(total_cost, 2)
                booking.status = 'PENDING'
                booking.save()
                return redirect('payments:payment_page', booking_id=booking.booking_id)
    else:
        form = BookingForm(initial=initial)

    context = {
        'form': form,
        'package': package,
        'custom_trip': custom_trip,
        'quotation': quotation,
        'package_id': package_param,
        'custom_trip_id': trip_param,
    }
    context.update(price_context)
    return render(request, 'bookings/checkout.html', context)


@login_required
def recalc_custom_trip_price_htmx(request, custom_trip_id):
    if request.method != 'POST':
        return HttpResponse(status=405)

    from apps.custom_trips.models import CustomTrip
    custom_trip = get_object_or_404(CustomTrip, id=custom_trip_id, user=request.user)

    raw_adults = _parse_raw_int(request.POST.get('adults', custom_trip.adults or 1), 1)
    raw_children = _parse_raw_int(request.POST.get('children', custom_trip.children or 0), 0)
    raw_infants = _parse_raw_int(request.POST.get('infants', custom_trip.infants or 0), 0)
    raw_days = _parse_raw_int(request.POST.get('total_days', custom_trip.total_days or 1), 1)

    validation_errors = []
    if raw_days < 1:
        validation_errors.append('Number of days must be at least 1.')
    if raw_adults < 1:
        validation_errors.append('There must be at least 1 adult.')
    if raw_children < 0:
        validation_errors.append('Number of children cannot be negative.')
    if raw_infants < 0:
        validation_errors.append('Number of infants cannot be negative.')
    if (raw_adults + raw_children + raw_infants) < 1:
        validation_errors.append('There must be at least 1 traveler.')

    days = max(1, raw_days)
    adults = max(1, raw_adults)
    children = max(0, raw_children)
    infants = max(0, raw_infants)

    breakdown = _calculate_custom_trip_price(custom_trip, days=days, adults=adults, children=children)
    grand_total = breakdown['grand_total']

    if grand_total <= Decimal('0'):
        validation_errors.append('Total booking amount must be greater than 0.')

    partial_amount = grand_total * Decimal('0.30')
    balance_amount = grand_total - partial_amount

    if not validation_errors and grand_total > Decimal('0'):
        custom_trip.adults = adults
        custom_trip.children = children
        custom_trip.infants = infants
        custom_trip.total_days = days
        custom_trip.total_calculated_price = grand_total
        custom_trip.save()
        td_list = list(custom_trip.trip_destinations.all())
        if len(td_list) == 1:
            td_list[0].days_stay = days
            td_list[0].save()

    context = {
        'custom_trip': custom_trip,
        'is_custom_trip': True,
        'base_price': breakdown['base_price'],
        'extra_days_price': breakdown['extra_days_price'],
        'activity_adult_total': breakdown['activity_adult_total'],
        'activity_child_total': breakdown['activity_child_total'],
        'activities_total': breakdown['activities_total'],
        'transport_total': breakdown['transport_total'],
        'hotel_total': breakdown['hotel_total'],
        'subtotal': breakdown['subtotal'],
        'service_charge': breakdown['service_charge'],
        'vat': breakdown['vat'],
        'grand_total': grand_total,
        'partial_amount': partial_amount,
        'balance_amount': balance_amount,
        'validation_errors': validation_errors,
        'adults': adults,
        'children': children,
        'infants': infants,
        'days': days,
    }

    html = render_to_string(
        'bookings/partials/checkout_price_summary.html',
        context,
        request=request,
    )
    return HttpResponse(html)


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    progress_steps = booking.get_progress_steps()
    progress_percentage = booking.get_progress_percentage()

    context = {
        'booking': booking,
        'progress_steps': progress_steps,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'bookings/detail.html', context)


@login_required
def booking_success(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    context = {
        'booking': booking,
        'message': f'Booking {booking.booking_id} has been created successfully!',
    }
    return render(request, 'bookings/success.html', context)


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, f'Booking {booking.booking_id} has been cancelled.')
        return redirect('accounts:my_bookings')
    return redirect('bookings:booking_detail', pk=pk)


@login_required
def download_itinerary(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    itinerary_content = booking.generate_itinerary_text()

    response = HttpResponse(itinerary_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="itinerary_{booking.booking_id}.txt"'
    return response
