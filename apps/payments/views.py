from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal

from apps.bookings.models import Booking
from apps.tickets.models import StandaloneTicket
from .models import Payment
from .forms import PaymentForm


@login_required
def payment_page(request, booking_id):
    if str(booking_id).isdigit():
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    else:
        booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.booking = booking

            payment_option = form.cleaned_data.get('payment_option', 'FULL')
            if payment_option == 'PARTIAL_30':
                payment.amount = Decimal(str(booking.total_cost)) * Decimal('0.30')
            else:
                payment.amount = Decimal(str(booking.total_cost))

            payment_method = form.cleaned_data.get('payment_method')
            if payment_method in ('ESEWA', 'KHALTI'):
                import uuid
                payment.transaction_ref = f'{payment_method}-{uuid.uuid4().hex[:12].upper()}'
            elif payment_method == 'BANK_TRANSFER':
                if not payment.payment_receipt:
                    messages.error(request, 'Payment receipt is required for bank transfer.')
                    return render(request, 'payments/payment_page.html', {
                        'form': form,
                        'booking': booking,
                        'total_cost': booking.total_cost,
                    })

            payment.verification_status = 'PENDING'
            payment.save()

            messages.success(request, 'Payment submitted successfully. Awaiting verification.')
            return redirect('payments:payment_success', pk=payment.pk)
    else:
        form = PaymentForm()

    return render(request, 'payments/payment_page.html', {
        'form': form,
        'booking': booking,
        'total_cost': booking.total_cost,
    })


@login_required
def ticket_payment_page(request, ticket_id):
    if str(ticket_id).isdigit():
        ticket = get_object_or_404(StandaloneTicket, id=ticket_id, user=request.user)
    else:
        ticket = get_object_or_404(StandaloneTicket, ticket_number=ticket_id, user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.ticket = ticket

            payment_option = form.cleaned_data.get('payment_option', 'FULL')
            if payment_option == 'PARTIAL_30':
                payment.amount = Decimal(str(ticket.total_price)) * Decimal('0.30')
            else:
                payment.amount = Decimal(str(ticket.total_price))

            payment_method = form.cleaned_data.get('payment_method')
            if payment_method in ('ESEWA', 'KHALTI'):
                import uuid
                payment.transaction_ref = f'{payment_method}-{uuid.uuid4().hex[:12].upper()}'
            elif payment_method == 'BANK_TRANSFER':
                if not payment.payment_receipt:
                    messages.error(request, 'Payment receipt is required for bank transfer.')
                    return render(request, 'payments/ticket_payment_page.html', {
                        'form': form,
                        'ticket': ticket,
                        'total_cost': ticket.total_price,
                    })

            payment.verification_status = 'PENDING'
            payment.save()

            messages.success(request, 'Payment submitted successfully. Awaiting verification.')
            return redirect('payments:payment_success', pk=payment.pk)
    else:
        form = PaymentForm()

    return render(request, 'payments/ticket_payment_page.html', {
        'form': form,
        'ticket': ticket,
        'total_cost': ticket.total_price,
    })


@login_required
def payment_success(request, pk):
    payment = get_object_or_404(Payment, pk=pk, user=request.user)
    return render(request, 'payments/payment_success.html', {
        'payment': payment,
    })


@staff_member_required
def verify_payment(request, pk):
    if request.method != 'POST':
        return redirect('admin:payments_payment_changelist')

    payment = get_object_or_404(Payment, pk=pk)
    payment.verification_status = 'APPROVED'
    payment.verified_by = request.user
    payment.verified_at = timezone.now()

    if payment.booking:
        payment.booking.payment_verified = True
        payment.booking.status = 'CONFIRMED'
        payment.booking.amount_paid = payment.amount
        payment.booking.save()

    payment.save()
    messages.success(request, f'Payment {payment.payment_ref} has been approved.')
    return redirect('admin:payments_payment_changelist')


@staff_member_required
def reject_payment(request, pk):
    if request.method != 'POST':
        return redirect('admin:payments_payment_changelist')

    payment = get_object_or_404(Payment, pk=pk)
    payment.verification_status = 'REJECTED'
    payment.admin_remarks = request.POST.get('admin_remarks', '')
    payment.verified_by = request.user
    payment.verified_at = timezone.now()
    payment.save()

    messages.warning(request, f'Payment {payment.payment_ref} has been rejected.')
    return redirect('admin:payments_payment_changelist')
