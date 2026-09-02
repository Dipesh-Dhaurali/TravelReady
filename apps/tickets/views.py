from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from .models import StandaloneTicket, TicketSchedule, TICKET_TYPE
from .forms import TicketSearchForm, TicketBookingForm


def ticket_list(request):
    schedules = TicketSchedule.objects.filter(is_active=True)
    schedules_by_type = {}
    for type_code, type_label in TICKET_TYPE:
        schedules_by_type[type_label] = schedules.filter(ticket_type=type_code)
    return render(request, 'tickets/list.html', {'schedules_by_type': schedules_by_type})


def ticket_search(request):
    form = TicketSearchForm(request.GET or None)
    schedules = TicketSchedule.objects.filter(is_active=True)

    if form.is_valid():
        ticket_type = form.cleaned_data.get('ticket_type')
        origin = form.cleaned_data.get('origin')
        destination = form.cleaned_data.get('destination')

        if ticket_type:
            schedules = schedules.filter(ticket_type=ticket_type)
        if origin:
            schedules = schedules.filter(origin__icontains=origin)
        if destination:
            schedules = schedules.filter(destination__icontains=destination)

    return render(request, 'tickets/search.html', {'form': form, 'schedules': schedules})


def ticket_book(request, schedule_id):
    schedule = get_object_or_404(TicketSchedule, id=schedule_id, is_active=True)

    if request.method == 'POST':
        form = TicketBookingForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.schedule_id = schedule_id
            ticket.ticket_type = schedule.ticket_type
            ticket.operator_name = schedule.operator_name
            ticket.origin = schedule.origin
            ticket.destination = schedule.destination
            ticket.travel_date = form.cleaned_data.get('travel_date') or None
            ticket.travel_time = schedule.departure_time
            ticket.price_per_person = schedule.price_per_person
            ticket.total_price = schedule.price_per_person * ticket.passenger_count
            if request.user.is_authenticated:
                ticket.user = request.user
            ticket.save()

            if ticket.user:
                messages.success(request, 'Ticket booked successfully. Please complete payment.')
                return redirect('tickets:ticket_detail', pk=ticket.pk)
            else:
                messages.success(request, 'Ticket booked successfully.')
                return redirect('tickets:ticket_detail', pk=ticket.pk)
    else:
        form = TicketBookingForm()

    return render(request, 'tickets/book.html', {'form': form, 'schedule': schedule})


@login_required
def my_tickets(request):
    tickets = StandaloneTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})


def ticket_detail(request, pk):
    ticket = get_object_or_404(StandaloneTicket, pk=pk)
    return render(request, 'tickets/detail.html', {'ticket': ticket})


def download_ticket(request, pk):
    ticket = get_object_or_404(StandaloneTicket, pk=pk)
    content = (
        f"Ticket Number: {ticket.ticket_number}\n"
        f"Ticket Type: {ticket.get_ticket_type_display()}\n"
        f"Operator: {ticket.operator_name}\n"
        f"Route: {ticket.origin} -> {ticket.destination}\n"
        f"Travel Date: {ticket.travel_date}\n"
        f"Travel Time: {ticket.travel_time or 'N/A'}\n"
        f"Return Date: {ticket.return_date or 'N/A'}\n"
        f"Passenger Count: {ticket.passenger_count}\n"
        f"Passenger Names: {ticket.passenger_names or 'N/A'}\n"
        f"Seat Numbers: {ticket.seat_numbers or 'N/A'}\n"
        f"Price Per Person: {ticket.price_per_person}\n"
        f"Total Price: {ticket.total_price}\n"
        f"Status: {ticket.get_status_display()}\n"
        f"Payment Verified: {'Yes' if ticket.payment_verified else 'No'}\n"
        f"Booked On: {ticket.created_at}\n"
    )
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.ticket_number}.txt"'
    return response
