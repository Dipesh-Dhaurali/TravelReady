from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from .models import Booking
from .forms import BookingForm


from decimal import Decimal


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
        from apps.destinations.models import Destination
        trip_destinations = custom_trip.trip_destinations.select_related('destination').all()
        days = custom_trip.total_days or 1
        adults = custom_trip.adults or 1
        children = custom_trip.children or 0

        package_multipliers = {
            'SINGLE': Decimal('1.0'),
            'COUPLE': Decimal('1.8'),
            'FAMILY': Decimal('2.5'),
        }
        multiplier = package_multipliers.get(custom_trip.package_type, Decimal('1.0'))

        base_price_total = Decimal('0')
        extra_days_price_total = Decimal('0')
        for td in trip_destinations:
            dest = td.destination
            dest_days = td.days_stay or max(1, days // len(trip_destinations)) if trip_destinations else days
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
        valid_hotel_categories = [c[0] for c in CustomTrip.HOTEL_CATEGORY_CHOICES]
        if (custom_trip.selected_hotel_category
                and custom_trip.selected_hotel_category in valid_hotel_categories
                and trip_destinations):
            cat = custom_trip.selected_hotel_category
            for td in trip_destinations:
                hotel = td.destination.hotels.filter(category=cat).first()
                if hotel:
                    stay = td.days_stay or (days // len(trip_destinations))
                    hotel_total += hotel.per_night_rate * Decimal(max(1, stay - 1))

        subtotal = base_cost + hotel_total + activities_total + transport_total
        service_charge = subtotal * Decimal('0.10')
        vat = (subtotal + service_charge) * Decimal('0.13')
        grand_total = subtotal + service_charge + vat

        if custom_trip.total_calculated_price and custom_trip.total_calculated_price > 0:
            grand_total_display = custom_trip.total_calculated_price
        else:
            grand_total_display = grand_total

        scaling = Decimal('1.0')
        if grand_total > 0:
            scaling = Decimal(grand_total_display) / grand_total

        partial_amount = grand_total_display * Decimal('0.30')
        balance_amount = grand_total_display - partial_amount

        price_context = {
            'is_custom_trip': True,
            'base_price': base_price_total * scaling,
            'extra_days_price': extra_days_price_total * scaling,
            'activity_adult_total': activity_adult_total_per * scaling,
            'activity_child_total': activity_child_total_per * scaling,
            'activities_total': activities_total * scaling,
            'transport_total': transport_total * scaling,
            'hotel_total': hotel_total * scaling,
            'subtotal': subtotal * scaling,
            'service_charge': service_charge * scaling,
            'vat': vat * scaling,
            'grand_total': grand_total_display,
            'partial_amount': partial_amount,
            'balance_amount': balance_amount,
        }
    elif package:
        price_context = {
            'is_custom_trip': False,
        }
    elif quotation:
        price_context = {
            'is_custom_trip': False,
            'grand_total': Decimal(str(quotation.admin_quoted_price or quotation.budget or 0)),
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
                base_cost = Decimal(str(custom_trip.total_calculated_price or price_context.get('grand_total', 0)))
            elif quotation:
                q_price = quotation.admin_quoted_price or quotation.budget or 0
                base_cost = Decimal(str(q_price))

            if custom_trip:
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
