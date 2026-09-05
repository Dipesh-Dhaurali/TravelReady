from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.destinations.models import (
    Destination,
    Hotel,
    Activity,
    Transportation,
)

from .models import (
    CustomTrip,
    CustomTripDestination,
    CustomQuotationRequest,
)
from .forms import CustomQuotationForm


@login_required
def trip_builder(request):
    destinations = Destination.objects.filter(status='Active')
    activities = Activity.objects.filter(is_available=True)
    transportations = Transportation.objects.all()
    hotel_categories = Hotel.CATEGORY_CHOICES

    context = {
        'destinations': destinations,
        'activities': activities,
        'transportations': transportations,
        'hotel_categories': hotel_categories,
    }
    return render(request, 'custom_trips/builder.html', context)


@login_required
def calculate_trip_htmx(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    destination_ids = request.POST.getlist('destinations[]')
    days_per_dest = request.POST.getlist('days_per_dest[]')
    hotel_category = request.POST.get('hotel_category', 'BUDGET')
    adults = int(request.POST.get('adults', 1) or 1)
    children = int(request.POST.get('children', 0) or 0)
    activity_ids = request.POST.getlist('activities[]')
    transport_ids = request.POST.getlist('transport[]')

    total_people = adults + children

    hotel_cost_total = Decimal('0')
    destination_breakdown = []
    total_days = 0

    for idx, dest_id in enumerate(destination_ids):
        try:
            destination = Destination.objects.get(id=dest_id, status='Active')
            days = int(days_per_dest[idx]) if idx < len(days_per_dest) else 2
            total_days += days

            nights = days - 1 if days > 1 else 1

            hotel = destination.hotels.filter(category=hotel_category).first()
            hotel_cost = Decimal('0')
            if hotel:
                hotel_cost = hotel.per_night_rate * Decimal(nights) * Decimal(max(total_people, 1))
                hotel_cost_total += hotel_cost

            destination_breakdown.append({
                'destination': destination,
                'days': days,
                'nights': nights,
                'hotel': hotel,
                'hotel_cost': hotel_cost,
            })
        except Destination.DoesNotExist:
            continue

    activities_cost = Decimal('0')
    selected_activity_objs = []
    if activity_ids:
        activity_qs = Activity.objects.filter(
            id__in=activity_ids,
            is_available=True,
        )
        for act in activity_qs:
            selected_activity_objs.append(act)
            activities_cost += (act.adult_price * Decimal(adults)) + (
                act.child_price * Decimal(children)
            )

    transport_cost = Decimal('0')
    selected_transport_objs = []
    if transport_ids:
        transport_qs = Transportation.objects.filter(id__in=transport_ids)
        for trans in transport_qs:
            selected_transport_objs.append(trans)
            if trans.per_vehicle_price and trans.per_vehicle_price > 0:
                transport_cost += trans.per_vehicle_price
            else:
                transport_cost += trans.per_person_price * Decimal(
                    max(total_people, 1)
                )

    subtotal = hotel_cost_total + activities_cost + transport_cost
    service_charge_rate = Decimal('0.10')
    service_charge = subtotal * service_charge_rate
    tax_rate = Decimal('0.13')
    tax = (subtotal + service_charge) * tax_rate
    grand_total = subtotal + service_charge + tax

    breakdown = {
        'destination_breakdown': destination_breakdown,
        'total_days': total_days,
        'hotel_category': hotel_category,
        'adults': adults,
        'children': children,
        'total_people': total_people,
        'hotel_cost_total': hotel_cost_total,
        'activities': selected_activity_objs,
        'activities_cost': activities_cost,
        'transportations': selected_transport_objs,
        'transport_cost': transport_cost,
        'subtotal': subtotal,
        'service_charge_rate': service_charge_rate * 100,
        'service_charge': service_charge,
        'tax_rate': tax_rate * 100,
        'tax': tax,
        'grand_total': grand_total,
    }

    html = render_to_string(
        'custom_trips/partials/price_breakdown.html',
        breakdown,
        request=request,
    )
    return HttpResponse(html)


@login_required
def save_custom_trip(request):
    if request.method != 'POST':
        return redirect('custom_trips:trip_builder')

    trip_name = request.POST.get('trip_name', 'My Custom Trip')
    hotel_category = request.POST.get('selected_hotel_category', 'BUDGET')
    adults = int(request.POST.get('adults', 1) or 1)
    children = int(request.POST.get('children', 0) or 0)
    infants = int(request.POST.get('infants', 0) or 0)
    notes = request.POST.get('notes', '')
    destination_ids = request.POST.getlist('destinations[]')
    days_per_dest = request.POST.getlist('days_per_dest[]')
    activity_ids = request.POST.getlist('selected_activities[]')
    transport_ids = request.POST.getlist('selected_transportation[]')
    total_price = Decimal(request.POST.get('total_calculated_price', '0') or '0')
    total_days = int(request.POST.get('total_days', '0') or '0')

    custom_trip = CustomTrip.objects.create(
        trip_name=trip_name,
        user=request.user,
        total_days=total_days,
        selected_hotel_category=hotel_category,
        adults=adults,
        children=children,
        infants=infants,
        total_calculated_price=total_price,
        status='SAVED',
        notes=notes,
    )

    for idx, dest_id in enumerate(destination_ids):
        try:
            destination = Destination.objects.get(id=dest_id)
            days = int(days_per_dest[idx]) if idx < len(days_per_dest) else 2
            CustomTripDestination.objects.create(
                custom_trip=custom_trip,
                destination=destination,
                order=idx + 1,
                days_stay=days,
            )
        except Destination.DoesNotExist:
            continue

    if activity_ids:
        custom_trip.selected_activities.set(activity_ids)
    if transport_ids:
        custom_trip.selected_transportation.set(transport_ids)

    messages.success(request, 'Custom trip saved successfully!')
    return redirect('custom_trips:custom_trip_detail', pk=custom_trip.pk)


@login_required
def my_custom_trips(request):
    trips = CustomTrip.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'trips': trips,
    }
    return render(request, 'custom_trips/my_trips.html', context)


@login_required
def custom_trip_detail(request, pk):
    trip = get_object_or_404(CustomTrip, pk=pk, user=request.user)
    trip_destinations = trip.trip_destinations.all()
    selected_activities = trip.selected_activities.all()
    selected_transportation = trip.selected_transportation.all()

    context = {
        'trip': trip,
        'trip_destinations': trip_destinations,
        'selected_activities': selected_activities,
        'selected_transportation': selected_transportation,
    }
    return render(request, 'custom_trips/detail.html', context)


@login_required
def book_custom_trip(request, pk):
    trip = get_object_or_404(CustomTrip, pk=pk, user=request.user)
    checkout_url = reverse('bookings:booking_checkout') + f'?custom_trip={trip.pk}'
    return redirect(checkout_url)


@login_required
def quotation_request(request):
    if request.method == 'POST':
        form = CustomQuotationForm(request.POST)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.user = request.user
            quotation.save()
            messages.success(request, 'Quote request submitted successfully!')
            return redirect('custom_trips:quotation_detail', pk=quotation.pk)
    else:
        form = CustomQuotationForm()

    context = {
        'form': form,
    }
    return render(request, 'custom_trips/quotation_request.html', context)


@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(CustomQuotationRequest, pk=pk, user=request.user)
    context = {
        'quotation': quotation,
    }
    return render(request, 'custom_trips/quotation_detail.html', context)


@login_required
def quotation_accept(request, pk):
    quotation = get_object_or_404(CustomQuotationRequest, pk=pk, user=request.user)
    if quotation.status == 'QUOTED':
        quotation.status = 'ACCEPTED'
        quotation.save()
        messages.success(request, 'Quotation accepted! We will contact you shortly.')
    else:
        messages.warning(request, 'Only quoted quotations can be accepted.')
    return redirect('custom_trips:quotation_detail', pk=quotation.pk)
