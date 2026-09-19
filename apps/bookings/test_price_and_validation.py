from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta

from apps.destinations.models import Destination, Hotel, Activity, Transportation
from apps.custom_trips.models import CustomTrip, CustomTripDestination
from apps.destinations.views import (
    calculate_destination_price,
    validate_destination_inputs,
    PACKAGE_MULTIPLIERS,
)
from apps.bookings.views import _calculate_custom_trip_price
from apps.bookings.forms import BookingForm


class PriceCalculationAndValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()
        self.client.login(username='testuser', password='password123')

        self.destination = Destination.objects.create(
            name='Pokhara Test',
            slug='pokhara-test',
            description='Test description',
            base_visit_cost=Decimal('5000.00'),
            status='Active',
        )

        self.hotel_budget = Hotel.objects.create(
            destination=self.destination,
            name='Budget Inn',
            category='BUDGET',
            per_night_rate=Decimal('2000.00'),
        )

        self.activity_boating = Activity.objects.create(
            destination=self.destination,
            title='Boating',
            adult_price=Decimal('500.00'),
            child_price=Decimal('250.00'),
            is_available=True,
        )

        self.transport_car = Transportation.objects.create(
            destination=self.destination,
            vehicle_type='CAR',
            route_origin='Kathmandu',
            per_vehicle_price=Decimal('4000.00'),
            per_person_price=Decimal('0.00'),
        )

    def test_destination_price_adults_change(self):
        # 3 days, 2 adults -> 3 to 4 days, adult 2 to 3
        # Single person package: multiplier = 1.0
        # 3 days = 1 base day + 2 extra days = 5000 + 2*5000 = 15000 base cost
        # Hotel budget for 3 days = 2 nights * 2000 = 4000
        # Boating for 2 adults = 2 * 500 = 1000
        # Transport = 4000
        # Subtotal = 15000 + 4000 + 1000 + 4000 = 24000
        # Service Charge 10% = 2400
        # VAT 13% = (24000 + 2400) * 0.13 = 3432
        # Grand Total = 29832
        calc_2_adults = calculate_destination_price(
            destination=self.destination,
            days=3,
            package_type='SINGLE',
            adults=2,
            children=0,
            hotel_category='BUDGET',
            selected_activities=[str(self.activity_boating.id)],
            selected_transport=[str(self.transport_car.id)],
        )
        self.assertEqual(calc_2_adults['base_cost'], Decimal('15000.00'))
        self.assertEqual(calc_2_adults['hotel_total'], Decimal('4000.00'))
        self.assertEqual(calc_2_adults['activities_total'], Decimal('1000.00'))
        self.assertEqual(calc_2_adults['transport_total'], Decimal('4000.00'))
        self.assertEqual(calc_2_adults['subtotal'], Decimal('24000.00'))
        self.assertEqual(calc_2_adults['grand_total'], Decimal('29832.00'))

        # Now change adult 2 to 3:
        # Boating becomes 3 * 500 = 1500 (+500)
        # Subtotal = 24500
        # SC = 2450
        # VAT = (24500 + 2450) * 0.13 = 3503.50
        # Grand Total = 30453.50
        calc_3_adults = calculate_destination_price(
            destination=self.destination,
            days=3,
            package_type='SINGLE',
            adults=3,
            children=0,
            hotel_category='BUDGET',
            selected_activities=[str(self.activity_boating.id)],
            selected_transport=[str(self.transport_car.id)],
        )
        self.assertEqual(calc_3_adults['activities_total'], Decimal('1500.00'))
        self.assertEqual(calc_3_adults['subtotal'], Decimal('24500.00'))
        self.assertEqual(calc_3_adults['grand_total'], Decimal('30453.50'))

    def test_destination_price_days_change(self):
        # Change days 3 to 4:
        # Base: 4 days = 1 base + 3 extra = 5000 + 3*5000 = 20000 (+5000)
        # Hotel: 4 days = 3 nights * 2000 = 6000 (+2000)
        calc_4_days = calculate_destination_price(
            destination=self.destination,
            days=4,
            package_type='SINGLE',
            adults=2,
            children=0,
            hotel_category='BUDGET',
            selected_activities=[str(self.activity_boating.id)],
            selected_transport=[str(self.transport_car.id)],
        )
        self.assertEqual(calc_4_days['base_cost'], Decimal('20000.00'))
        self.assertEqual(calc_4_days['hotel_total'], Decimal('6000.00'))
        self.assertEqual(calc_4_days['subtotal'], Decimal('31000.00'))

        # Change days 4 to 3: should match 24000 subtotal again
        calc_3_days = calculate_destination_price(
            destination=self.destination,
            days=3,
            package_type='SINGLE',
            adults=2,
            children=0,
            hotel_category='BUDGET',
            selected_activities=[str(self.activity_boating.id)],
            selected_transport=[str(self.transport_car.id)],
        )
        self.assertEqual(calc_3_days['subtotal'], Decimal('24000.00'))

    def test_destination_validation_rules(self):
        # Adults cannot be less than 1
        errors = validate_destination_inputs(days=3, adults=0, children=0)
        self.assertIn('There must be at least 1 adult.', errors)

        errors = validate_destination_inputs(days=3, adults=-2, children=0)
        self.assertIn('There must be at least 1 adult.', errors)

        # Days cannot be less than 1
        errors = validate_destination_inputs(days=0, adults=2, children=0)
        self.assertIn('Number of days must be at least 1.', errors)

        errors = validate_destination_inputs(days=-1, adults=2, children=0)
        self.assertIn('Number of days must be at least 1.', errors)

        # Children can be 0, but not negative
        errors = validate_destination_inputs(days=3, adults=2, children=0)
        self.assertEqual(len(errors), 0)

        errors = validate_destination_inputs(days=3, adults=2, children=-1)
        self.assertIn('Number of children cannot be negative.', errors)

    def test_custom_trip_price_calculation_parity(self):
        # Create CustomTrip matching the destination
        trip = CustomTrip.objects.create(
            user=self.user,
            trip_name='Pokhara Test Trip',
            package_type='SINGLE',
            total_days=3,
            adults=2,
            children=0,
            selected_hotel_category='BUDGET',
            status='SAVED',
        )
        CustomTripDestination.objects.create(
            custom_trip=trip,
            destination=self.destination,
            days_stay=3,
            order=1,
        )
        trip.selected_activities.set([self.activity_boating])
        trip.selected_transportation.set([self.transport_car])

        # CustomTrip calculation for 3 days, 2 adults
        custom_calc = _calculate_custom_trip_price(trip, days=3, adults=2, children=0)
        dest_calc = calculate_destination_price(
            destination=self.destination,
            days=3,
            package_type='SINGLE',
            adults=2,
            children=0,
            hotel_category='BUDGET',
            selected_activities=[str(self.activity_boating.id)],
            selected_transport=[str(self.transport_car.id)],
        )
        # Parity check: every single item must match exactly!
        self.assertEqual(custom_calc['base_price'], dest_calc['base_price'])
        self.assertEqual(custom_calc['extra_days_price'], dest_calc['extra_days_price'])
        self.assertEqual(custom_calc['hotel_total'], dest_calc['hotel_total'])
        self.assertEqual(custom_calc['activities_total'], dest_calc['activities_total'])
        self.assertEqual(custom_calc['transport_total'], dest_calc['transport_total'])
        self.assertEqual(custom_calc['subtotal'], dest_calc['subtotal'])
        self.assertEqual(custom_calc['service_charge'], dest_calc['service_charge'])
        self.assertEqual(custom_calc['vat'], dest_calc['vat'])
        self.assertEqual(custom_calc['grand_total'], dest_calc['grand_total'])

        # Parity check when days changed to 4 and adults to 3 on custom trip
        custom_calc_4d_3a = _calculate_custom_trip_price(trip, days=4, adults=3, children=0)
        dest_calc_4d_3a = calculate_destination_price(
            destination=self.destination,
            days=4,
            package_type='SINGLE',
            adults=3,
            children=0,
            hotel_category='BUDGET',
            selected_activities=[str(self.activity_boating.id)],
            selected_transport=[str(self.transport_car.id)],
        )
        self.assertEqual(custom_calc_4d_3a['grand_total'], dest_calc_4d_3a['grand_total'])

    def test_recalc_custom_trip_endpoint_live_updates_and_validation(self):
        trip = CustomTrip.objects.create(
            user=self.user,
            trip_name='Pokhara Test Trip',
            package_type='SINGLE',
            total_days=3,
            adults=2,
            children=0,
            selected_hotel_category='BUDGET',
            status='SAVED',
        )
        CustomTripDestination.objects.create(
            custom_trip=trip,
            destination=self.destination,
            days_stay=3,
            order=1,
        )

        url = reverse('bookings:recalc_custom_trip_price', kwargs={'custom_trip_id': trip.id})

        # Test live adult change 2 to 3
        response = self.client.post(url, {'adults': '3', 'children': '0', 'infants': '0', 'total_days': '3'})
        self.assertEqual(response.status_code, 200)
        trip.refresh_from_db()
        self.assertEqual(trip.adults, 3)

        # Test live days change 3 to 4
        response = self.client.post(url, {'adults': '3', 'children': '0', 'infants': '0', 'total_days': '4'})
        self.assertEqual(response.status_code, 200)
        trip.refresh_from_db()
        self.assertEqual(trip.total_days, 4)

        # Test invalid adult 0 -> returns error in HTML, trip not updated
        response = self.client.post(url, {'adults': '0', 'children': '0', 'infants': '0', 'total_days': '4'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There must be at least 1 adult.')

        # Test invalid days 0 -> returns error in HTML
        response = self.client.post(url, {'adults': '2', 'children': '0', 'infants': '0', 'total_days': '0'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Number of days must be at least 1.')

        # Test negative children -> returns error in HTML
        response = self.client.post(url, {'adults': '2', 'children': '-1', 'infants': '0', 'total_days': '3'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Number of children cannot be negative.')

    def test_booking_form_validation(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Travel date in past
        form = BookingForm(data={
            'travel_date': yesterday.isoformat(),
            'return_date': tomorrow.isoformat(),
            'adults': 1,
            'children': 0,
            'infants': 0,
            'payment_option': 'FULL',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('travel_date', form.errors)

        # Return date before travel date
        form = BookingForm(data={
            'travel_date': tomorrow.isoformat(),
            'return_date': today.isoformat(),
            'adults': 1,
            'children': 0,
            'infants': 0,
            'payment_option': 'FULL',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('return_date', form.errors)

        # Adults < 1
        form = BookingForm(data={
            'travel_date': tomorrow.isoformat(),
            'return_date': (tomorrow + timedelta(days=3)).isoformat(),
            'adults': 0,
            'children': 1,
            'infants': 0,
            'payment_option': 'FULL',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('adults', form.errors)

        # Emergency contact phone not 10 digits
        form = BookingForm(data={
            'travel_date': tomorrow.isoformat(),
            'return_date': (tomorrow + timedelta(days=3)).isoformat(),
            'adults': 2,
            'children': 0,
            'infants': 0,
            'emergency_contact_phone': '984123456',  # 9 digits
            'payment_option': 'FULL',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('emergency_contact_phone', form.errors)

        # Emergency contact phone exactly 10 digits -> valid!
        form = BookingForm(data={
            'travel_date': tomorrow.isoformat(),
            'return_date': (tomorrow + timedelta(days=3)).isoformat(),
            'adults': 2,
            'children': 0,
            'infants': 0,
            'emergency_contact_phone': '9841234567',  # 10 digits
            'payment_option': 'FULL',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_destination_htmx_live_calculation_and_validation(self):
        url = reverse('destinations:calculate_price_htmx', kwargs={'slug': self.destination.slug})

        # Test live adult change 2 to 3
        resp = self.client.post(url, {
            'package_type': 'SINGLE',
            'num_days': '3',
            'adults': '3',
            'children': '0',
            'hotel_category': 'BUDGET',
            'activities': [str(self.activity_boating.id)],
            'transportation': [str(self.transport_car.id)],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '30453.50')

        # Test live days change 3 to 4
        resp = self.client.post(url, {
            'package_type': 'SINGLE',
            'num_days': '4',
            'adults': '3',
            'children': '0',
            'hotel_category': 'BUDGET',
            'activities': [str(self.activity_boating.id)],
            'transportation': [str(self.transport_car.id)],
        })
        self.assertEqual(resp.status_code, 200)

        # Test invalid adult: 0
        resp_inv = self.client.post(url, {
            'package_type': 'SINGLE',
            'num_days': '3',
            'adults': '0',
            'children': '0',
        })
        self.assertEqual(resp_inv.status_code, 200)
        self.assertContains(resp_inv, 'There must be at least 1 adult.')

        # Test invalid days: 0
        resp_inv_days = self.client.post(url, {
            'package_type': 'SINGLE',
            'num_days': '0',
            'adults': '2',
            'children': '0',
        })
        self.assertEqual(resp_inv_days.status_code, 200)
        self.assertContains(resp_inv_days, 'Number of days must be at least 1.')

    def test_destination_book_now_redirect_and_validation(self):
        url = reverse('destinations:book_destination', kwargs={'slug': self.destination.slug})

        # Invalid post: adults=0
        resp = self.client.post(url, {
            'num_days': '3',
            'adults': '0',
            'children': '0',
        })
        self.assertEqual(resp.status_code, 302)
        # Should redirect back to destination detail, NOT to checkout
        self.assertNotIn('checkout', resp.url)

        # Valid post: adults=2, days=3
        resp = self.client.post(url, {
            'package_type': 'SINGLE',
            'num_days': '3',
            'adults': '2',
            'children': '0',
            'hotel_category': 'BUDGET',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('checkout', resp.url)

    def test_checkout_post_updates_custom_trip_and_saves_booking(self):
        trip = CustomTrip.objects.create(
            user=self.user,
            trip_name='Pokhara Test Trip',
            package_type='SINGLE',
            total_days=3,
            adults=2,
            children=0,
            selected_hotel_category='BUDGET',
            status='SAVED',
        )
        CustomTripDestination.objects.create(
            custom_trip=trip,
            destination=self.destination,
            days_stay=3,
            order=1,
        )

        checkout_url = reverse('bookings:booking_checkout') + f'?custom_trip={trip.id}'

        tomorrow = date.today() + timedelta(days=1)
        return_date = tomorrow + timedelta(days=4)

        # Submit checkout changing adults from 2 to 3 and days from 3 to 4
        post_data = {
            'travel_date': tomorrow.isoformat(),
            'return_date': return_date.isoformat(),
            'total_days': '4',
            'adults': '3',
            'children': '0',
            'infants': '0',
            'emergency_contact_phone': '9841234567',
            'payment_option': 'FULL',
        }
        resp = self.client.post(checkout_url, post_data)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('payment', resp.url)

        # Verify CustomTrip was updated to 3 adults and 4 days
        trip.refresh_from_db()
        self.assertEqual(trip.adults, 3)
        self.assertEqual(trip.total_days, 4)

        # Verify Booking was created with matching total
        from apps.bookings.models import Booking
        booking = Booking.objects.filter(user=self.user, custom_trip=trip).last()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.total_cost, trip.total_calculated_price)
        self.assertGreater(booking.total_cost, Decimal('0'))

