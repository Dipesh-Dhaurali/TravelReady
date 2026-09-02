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
                base_cost = Decimal(str(custom_trip.total_calculated_price))
            elif quotation:
                q_price = quotation.admin_quoted_price or quotation.budget or 0
                base_cost = Decimal(str(q_price))

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
        form = BookingForm()

    context = {
        'form': form,
        'package': package,
        'custom_trip': custom_trip,
        'quotation': quotation,
        'package_id': package_param,
        'custom_trip_id': trip_param,
    }
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
