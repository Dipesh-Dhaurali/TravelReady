from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile
from apps.bookings.models import Booking
from apps.custom_trips.models import CustomTrip, CustomQuotationRequest
from apps.tickets.models import StandaloneTicket
from apps.destinations.models import Destination, Wishlist
from apps.destinations.forms import DestinationForm
from apps.payments.models import Payment


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to your dashboard.')
            if user.is_staff or user.is_superuser:
                return redirect('dashboard:admin_dashboard')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('destinations_home:home')


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Profile update failed. Please correct the errors.')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})


@login_required
def dashboard_home(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    user = request.user
    bookings = Booking.objects.filter(user=user)
    custom_trips = CustomTrip.objects.filter(user=user, status='SAVED')
    quotations = CustomQuotationRequest.objects.filter(user=user)
    tickets = StandaloneTicket.objects.filter(user=user)
    wishlist_count = Wishlist.objects.filter(user=user).count()

    total_spent = Payment.objects.filter(
        user=user,
        verification_status='APPROVED'
    ).aggregate(total=Sum('amount'))['total'] or 0

    pending_payments_count = Booking.objects.filter(user=user, status='PENDING').count()
    pending_amount = Booking.objects.filter(user=user, status='PENDING').aggregate(total=Sum('total_cost'))['total'] or 0

    upcoming_bookings = bookings.filter(
        status__in=['CONFIRMED', 'TRIP_STARTED'],
        travel_date__gte=timezone.now().date()
    ).order_by('travel_date')
    upcoming_trips_count = upcoming_bookings.count()

    next_trip_days = None
    first_upcoming = upcoming_bookings.first()
    if first_upcoming and first_upcoming.travel_date:
        next_trip_days = (first_upcoming.travel_date - timezone.now().date()).days

    context = {
        'total_bookings': bookings.count(),
        'upcoming_trips': upcoming_trips_count,
        'next_trip_days': next_trip_days or 0,
        'pending_payments': pending_payments_count,
        'pending_amount': pending_amount,
        'saved_trips': wishlist_count or custom_trips.count(),
        'total_custom_trips': custom_trips.count(),
        'total_quotations': quotations.count(),
        'total_tickets': tickets.count(),
        'total_spent': total_spent,
        'upcoming_bookings': upcoming_bookings[:3],
        'recent_bookings': bookings.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')

    total_revenue = Payment.objects.filter(
        verification_status='APPROVED'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    total_users = UserProfile.objects.count()

    pending_payments = Payment.objects.filter(verification_status='PENDING').count()
    pending_quotations = CustomQuotationRequest.objects.filter(status='PENDING').count()

    recent_bookings = Booking.objects.order_by('-created_at')[:10]
    recent_payments = Payment.objects.order_by('-created_at')[:10]

    context = {
        'total_revenue': total_revenue,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_users': total_users,
        'pending_payments': pending_payments,
        'pending_quotations': pending_quotations,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/my_bookings.html', context)


@login_required
def my_trips(request):
    trips = CustomTrip.objects.filter(
        user=request.user
    ).order_by('-updated_at')
    context = {
        'trips': trips,
    }
    return render(request, 'dashboard/my_trips.html', context)


@login_required
def my_quotations(request):
    quotations = CustomQuotationRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')
    context = {
        'quotations': quotations,
    }
    return render(request, 'dashboard/my_quotations.html', context)


@login_required
def my_tickets(request):
    tickets = StandaloneTicket.objects.filter(
        user=request.user
    ).order_by('-created_at')
    context = {
        'tickets': tickets,
    }
    return render(request, 'dashboard/my_tickets.html', context)


@login_required
def my_itineraries(request):
    # Try to use a dedicated Itinerary model if it exists, fallback to bookings
    try:
        from apps.itinerary.models import Itinerary
        itineraries = Itinerary.objects.filter(user=request.user).order_by('-created_at')
    except ImportError:
        try:
            from apps.bookings.models import Itinerary
            itineraries = Itinerary.objects.filter(booking__user=request.user).order_by('-created_at')
        except (ImportError, AttributeError):
            itineraries = []
    context = {
        'itineraries': itineraries,
    }
    return render(request, 'dashboard/my_itineraries.html', context)


@login_required
def my_wishlist(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('destination').order_by('-added_at')
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'dashboard/my_wishlist.html', context)


@login_required
def profile_settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    user = request.user

    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        if form_type == 'profile':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            username = request.POST.get('username', user.username)
            if username and username != user.username:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(username=username).exclude(pk=user.pk).exists():
                    user.username = username
            user.save()

            profile.phone = request.POST.get('phone', profile.phone)
            profile.address = request.POST.get('address', profile.address)
            dob = request.POST.get('date_of_birth', '')
            if dob:
                try:
                    from datetime import date
                    profile.date_of_birth = dob
                except Exception:
                    pass
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile_settings')

        elif form_type == 'password':
            from django.contrib.auth import update_session_auth_hash
            current_password = request.POST.get('current_password', '')
            new_password1 = request.POST.get('new_password1', '')
            new_password2 = request.POST.get('new_password2', '')
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password1 != new_password2:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password1) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
            return redirect('dashboard:profile_settings')

    total_bookings = Booking.objects.filter(user=user).count()
    completed_trips = Booking.objects.filter(user=user, status='COMPLETED').count()
    wishlist_count = Wishlist.objects.filter(user=user).count()

    context = {
        'profile': profile,
        'total_bookings': total_bookings,
        'completed_trips': completed_trips,
        'saved_trips': wishlist_count,
    }
    return render(request, 'dashboard/profile_settings.html', context)


@login_required
def admin_destinations(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    destinations = Destination.objects.all().order_by('-created_at')
    context = {
        'destinations': destinations,
    }
    return render(request, 'dashboard/admin/destinations/list.html', context)


@login_required
def admin_destination_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            destination = form.save()
            messages.success(request, f'Destination "{destination.name}" created successfully!')
            return redirect('dashboard:admin_destinations')
        else:
            messages.error(request, 'Failed to create destination. Please check form errors.')
    else:
        form = DestinationForm()
    context = {'form': form}
    return render(request, 'dashboard/admin/destinations/create.html', context)


@login_required
def admin_destination_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            destination = form.save()
            messages.success(request, f'Destination "{destination.name}" updated successfully!')
            return redirect('dashboard:admin_destinations')
        else:
            messages.error(request, 'Failed to update destination. Please check form errors.')
    else:
        form = DestinationForm(instance=destination)
    context = {'destination': destination, 'form': form}
    return render(request, 'dashboard/admin/destinations/edit.html', context)


@login_required
def admin_destination_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    destination = get_object_or_404(Destination, pk=pk)
    if request.method == 'POST':
        name = destination.name
        destination.delete()
        messages.success(request, f'Destination "{name}" deleted successfully.')
        return redirect('dashboard:admin_destinations')
    context = {'destination': destination}
    return render(request, 'dashboard/admin/destinations/delete.html', context)


@login_required
def admin_bookings_list(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    bookings = Booking.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter != 'ALL':
        bookings = bookings.filter(status=status_filter)
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/admin/bookings/list.html', context)


@login_required
def admin_booking_detail(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        if status in dict(Booking.STATUS):
            booking.status = status
        booking.admin_notes = admin_notes
        booking.save()
        messages.success(request, f'Booking {booking.booking_id} updated successfully!')
        return redirect('dashboard:admin_booking_detail', pk=booking.pk)

    payments = Payment.objects.filter(booking=booking)
    context = {
        'booking': booking,
        'payments': payments,
    }
    return render(request, 'dashboard/admin/bookings/detail.html', context)


@login_required
def admin_quotations(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    quotations = CustomQuotationRequest.objects.all().order_by('-created_at')
    context = {
        'quotations': quotations,
    }
    return render(request, 'dashboard/admin/quotations/list.html', context)


@login_required
def admin_quotation_detail(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    quotation = get_object_or_404(CustomQuotationRequest, pk=pk)
    if request.method == 'POST':
        admin_quoted_price = request.POST.get('admin_quoted_price')
        admin_notes = request.POST.get('admin_notes', '')
        generated_itinerary = request.POST.get('generated_itinerary', '')
        status = request.POST.get('status', quotation.status)

        if admin_quoted_price:
            quotation.admin_quoted_price = admin_quoted_price
        quotation.admin_notes = admin_notes
        quotation.generated_itinerary = generated_itinerary
        quotation.status = status
        quotation.save()
        messages.success(request, 'Quotation updated successfully.')
        return redirect('dashboard:admin_quotations')
    context = {'quotation': quotation}
    return render(request, 'dashboard/admin/quotations/detail.html', context)


@login_required
def admin_payments(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    payments = Payment.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status') or request.GET.get('filter') or ''
    if status_filter and status_filter != 'ALL':
        payments = payments.filter(verification_status=status_filter)
    context = {
        'payments': payments,
        'status_filter': status_filter,
        'filter': status_filter,
    }
    return render(request, 'dashboard/admin/payments/list.html', context)


@login_required
def admin_payment_verify(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action', 'verify')
        admin_remarks = request.POST.get('admin_remarks', '')
        if action == 'verify':
            payment.verification_status = 'APPROVED'
            payment.verified_by = request.user
            payment.verified_at = timezone.now()
            if payment.booking:
                payment.booking.payment_verified = True
                payment.booking.status = 'CONFIRMED'
                payment.booking.amount_paid = payment.amount
                payment.booking.save()
            messages.success(request, 'Payment verified successfully.')
        else:
            payment.verification_status = 'REJECTED'
            payment.admin_remarks = admin_remarks
            payment.verified_by = request.user
            payment.verified_at = timezone.now()
            messages.warning(request, 'Payment rejected.')
        payment.save()
        return redirect('dashboard:admin_payments')
    context = {'payment': payment}
    return render(request, 'dashboard/admin/payments/verify.html', context)


@login_required
def admin_packages(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.packages.models import PredefinedPackage
    packages = PredefinedPackage.objects.all().order_by('-created_at')
    context = {
        'packages': packages,
    }
    return render(request, 'dashboard/admin/packages/list.html', context)


@login_required
def admin_package_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.packages.forms import PackageForm
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            messages.success(request, f'Package "{package.title}" created successfully!')
            return redirect('dashboard:admin_packages')
        else:
            messages.error(request, 'Failed to create package. Please check form errors.')
    else:
        form = PackageForm()
    context = {'form': form}
    return render(request, 'dashboard/admin/packages/create.html', context)


@login_required
def admin_package_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.packages.models import PredefinedPackage
    from apps.packages.forms import PackageForm
    package = get_object_or_404(PredefinedPackage, pk=pk)
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            package = form.save()
            messages.success(request, f'Package "{package.title}" updated successfully!')
            return redirect('dashboard:admin_packages')
        else:
            messages.error(request, 'Failed to update package. Please check form errors.')
    else:
        form = PackageForm(instance=package)
    context = {'package': package, 'form': form}
    return render(request, 'dashboard/admin/packages/edit.html', context)


@login_required
def admin_package_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.packages.models import PredefinedPackage
    package = get_object_or_404(PredefinedPackage, pk=pk)
    if request.method == 'POST':
        title = package.title
        package.delete()
        messages.success(request, f'Package "{title}" deleted successfully.')
        return redirect('dashboard:admin_packages')
    context = {'package': package}
    return render(request, 'dashboard/admin/packages/delete.html', context)


@login_required
def admin_hotels(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.destinations.models import Hotel
    hotels = Hotel.objects.all().select_related('destination').order_by('destination__name')
    context = {
        'hotels': hotels,
    }
    return render(request, 'dashboard/admin/hotels/list.html', context)


@login_required
def admin_hotel_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.destinations.forms import HotelForm
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" added successfully!')
            return redirect('dashboard:admin_hotels')
        else:
            messages.error(request, 'Failed to add hotel. Please check form errors.')
    else:
        form = HotelForm()
    context = {'form': form}
    return render(request, 'dashboard/admin/hotels/create.html', context)


@login_required
def admin_hotel_edit(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.destinations.models import Hotel
    from apps.destinations.forms import HotelForm
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" updated successfully!')
            return redirect('dashboard:admin_hotels')
        else:
            messages.error(request, 'Failed to update hotel. Please check form errors.')
    else:
        form = HotelForm(instance=hotel)
    context = {'hotel': hotel, 'form': form}
    return render(request, 'dashboard/admin/hotels/edit.html', context)


@login_required
def admin_hotel_delete(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard:dashboard')
    from apps.destinations.models import Hotel
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        name = hotel.name
        hotel.delete()
        messages.success(request, f'Hotel "{name}" deleted successfully.')
        return redirect('dashboard:admin_hotels')
    context = {'hotel': hotel}
    return render(request, 'dashboard/admin/hotels/delete.html', context)
