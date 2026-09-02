from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from apps.destinations.models import (
    Destination,
    Hotel,
    Activity,
    Transportation,
)
from apps.packages.models import PredefinedPackage


class Command(BaseCommand):
    help = 'Seed initial data for TravelReady project'

    def handle(self, *args, **options):
        destinations_created = 0
        hotels_created = 0
        activities_created = 0
        transports_created = 0
        packages_created = 0
        users_created = 0

        destinations_data = [
            {
                'name': 'Sauraha',
                'destination_type': 'INSIDE_COUNTRY',
                'location': 'Sauraha',
                'district': 'Chitwan',
                'description': 'Famous gateway to Chitwan National Park offering jungle safaris, elephant rides, canoe rides and Tharu culture experiences.',
                'base_visit_cost': Decimal('5000'),
                'best_season': 'October-March',
                'status': 'Active',
                'rules_regulations': 'Do not disturb wildlife. Follow guide instructions.',
            },
            {
                'name': 'Chitwan',
                'destination_type': 'INSIDE_COUNTRY',
                'location': 'Chitwan National Park',
                'district': 'Chitwan',
                'description': 'UNESCO World Heritage Site home to one-horned rhinos, Bengal tigers, crocodiles and 500+ bird species.',
                'base_visit_cost': Decimal('8000'),
                'best_season': 'October-April',
                'status': 'Active',
                'rules_regulations': '',
            },
            {
                'name': 'Pokhara',
                'destination_type': 'INSIDE_COUNTRY',
                'location': 'Pokhara',
                'district': 'Kaski',
                'description': 'Adventure capital with Phewa Lake, Annapurna mountain views, paragliding, zipline, and Davis Falls.',
                'base_visit_cost': Decimal('6000'),
                'best_season': 'October-April',
                'status': 'Active',
                'rules_regulations': '',
            },
            {
                'name': 'Kathmandu',
                'destination_type': 'INSIDE_COUNTRY',
                'location': 'Kathmandu Valley',
                'district': 'Kathmandu',
                'description': 'Cultural capital with UNESCO sites: Pashupatinath, Boudhanath, Swayambhunath, Durbar Squares.',
                'base_visit_cost': Decimal('4000'),
                'best_season': 'September-May',
                'status': 'Active',
                'rules_regulations': '',
            },
            {
                'name': 'Dubai',
                'destination_type': 'OUTSIDE_COUNTRY',
                'location': 'Dubai, UAE',
                'district': 'Dubai',
                'description': 'Luxury city with Burj Khalifa, desert safaris, palm islands, shopping malls and world-class hotels.',
                'base_visit_cost': Decimal('80000'),
                'best_season': 'November-March',
                'status': 'Active',
                'rules_regulations': '',
            },
            {
                'name': 'Bangkok',
                'destination_type': 'OUTSIDE_COUNTRY',
                'location': 'Bangkok, Thailand',
                'district': 'Bangkok',
                'description': 'Vibrant Thai capital with temples, floating markets, street food, nightlife and tropical beaches nearby.',
                'base_visit_cost': Decimal('60000'),
                'best_season': 'November-February',
                'status': 'Active',
                'rules_regulations': '',
            },
            {
                'name': 'Delhi',
                'destination_type': 'OUTSIDE_COUNTRY',
                'location': 'New Delhi, India',
                'district': 'Delhi',
                'description': 'Historic Indian capital with Red Fort, Qutub Minar, India Gate, Chandni Chowk bazaar and gateway to Taj Mahal.',
                'base_visit_cost': Decimal('25000'),
                'best_season': 'October-March',
                'status': 'Active',
                'rules_regulations': '',
            },
        ]

        created_destinations = {}
        for dest_data in destinations_data:
            try:
                dest, created = Destination.objects.get_or_create(
                    name=dest_data['name'],
                    defaults=dest_data,
                )
                created_destinations[dest.name] = dest
                if created:
                    destinations_created += 1
                    self.stdout.write(self.style.SUCCESS(f'Created destination: {dest.name}'))
                else:
                    self.stdout.write(f'Destination already exists: {dest.name}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating destination {dest_data["name"]}: {str(e)}'))

        hotels_data = {
            'Sauraha': [
                {'name': 'Sauraha Budget Lodge', 'category': 'BUDGET', 'per_night_rate': Decimal('2000')},
                {'name': 'Safari Lodge Sauraha', 'category': 'THREE_STAR', 'per_night_rate': Decimal('5000')},
                {'name': 'Jungle Villa Resort', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('10000')},
            ],
            'Chitwan': [
                {'name': 'Chitwan Budget Retreat', 'category': 'BUDGET', 'per_night_rate': Decimal('2500')},
                {'name': 'Rhino Lodge Chitwan', 'category': 'THREE_STAR', 'per_night_rate': Decimal('6000')},
                {'name': 'Tiger Palace Resort', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('12000')},
            ],
            'Pokhara': [
                {'name': 'Pokhara Budget Inn', 'category': 'BUDGET', 'per_night_rate': Decimal('2500')},
                {'name': 'Lakeside Star Hotel', 'category': 'THREE_STAR', 'per_night_rate': Decimal('6000')},
                {'name': 'Annapurna View Resort', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('12000')},
            ],
            'Kathmandu': [
                {'name': 'Thamel Budget Lodge', 'category': 'BUDGET', 'per_night_rate': Decimal('2000')},
                {'name': 'Kathmandu Garden Hotel', 'category': 'THREE_STAR', 'per_night_rate': Decimal('5000')},
                {'name': 'Valley View Palace', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('10000')},
            ],
            'Dubai': [
                {'name': 'Dubai Budget Stay', 'category': 'BUDGET', 'per_night_rate': Decimal('8000')},
                {'name': 'Dubai Downtown Hotel', 'category': 'THREE_STAR', 'per_night_rate': Decimal('20000')},
                {'name': 'Palm Luxury Resort', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('50000')},
            ],
            'Bangkok': [
                {'name': 'Bangkok Budget Guesthouse', 'category': 'BUDGET', 'per_night_rate': Decimal('6000')},
                {'name': 'Bangkok City Hotel', 'category': 'THREE_STAR', 'per_night_rate': Decimal('15000')},
                {'name': 'Grand Riverside Resort', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('40000')},
            ],
            'Delhi': [
                {'name': 'Delhi Budget Lodge', 'category': 'BUDGET', 'per_night_rate': Decimal('3000')},
                {'name': 'Connaught Place Hotel', 'category': 'THREE_STAR', 'per_night_rate': Decimal('8000')},
                {'name': 'New Delhi Heritage Resort', 'category': 'FOUR_STAR', 'per_night_rate': Decimal('20000')},
            ],
        }

        created_hotels = {}
        for dest_name, hotel_list in hotels_data.items():
            created_hotels[dest_name] = {}
            if dest_name not in created_destinations:
                continue
            dest = created_destinations[dest_name]
            for hotel_data in hotel_list:
                try:
                    hotel, created = Hotel.objects.get_or_create(
                        name=hotel_data['name'],
                        destination=dest,
                        defaults={
                            'category': hotel_data['category'],
                            'per_night_rate': hotel_data['per_night_rate'],
                            'room_types': 'Single,Double,Deluxe',
                        },
                    )
                    created_hotels[dest_name][hotel.category] = hotel
                    if created:
                        hotels_created += 1
                        self.stdout.write(self.style.SUCCESS(f'Created hotel: {hotel.name}'))
                    else:
                        self.stdout.write(f'Hotel already exists: {hotel.name}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating hotel {hotel_data["name"]}: {str(e)}'))

        activities_data = {
            'Sauraha': [
                {'title': 'Jungle Safari Walk', 'adult_price': Decimal('2000'), 'child_price': Decimal('1000'), 'duration_hours': Decimal('4.0')},
                {'title': 'Canoe Ride', 'adult_price': Decimal('1500'), 'child_price': Decimal('750'), 'duration_hours': Decimal('2.0')},
                {'title': 'Elephant Bath', 'adult_price': Decimal('1000'), 'child_price': Decimal('500'), 'duration_hours': Decimal('1.0')},
                {'title': 'Tharu Cultural Dance', 'adult_price': Decimal('800'), 'child_price': Decimal('400'), 'duration_hours': Decimal('1.5')},
            ],
            'Pokhara': [
                {'title': 'Boating Phewa Lake', 'adult_price': Decimal('1000'), 'child_price': Decimal('500'), 'duration_hours': Decimal('2.0')},
                {'title': 'Paragliding', 'adult_price': Decimal('8000'), 'child_price': Decimal('0'), 'duration_hours': Decimal('1.0')},
                {'title': 'Sarangkot Sunrise Tour', 'adult_price': Decimal('1500'), 'child_price': Decimal('750'), 'duration_hours': Decimal('3.0')},
                {'title': 'Zipline', 'adult_price': Decimal('3500'), 'child_price': Decimal('1750'), 'duration_hours': Decimal('1.5')},
            ],
            'Kathmandu': [
                {'title': 'Pashupatinath Tour', 'adult_price': Decimal('1000'), 'child_price': Decimal('500'), 'duration_hours': Decimal('2.0')},
                {'title': 'Chandragiri Cable Car', 'adult_price': Decimal('2000'), 'child_price': Decimal('1000'), 'duration_hours': Decimal('3.0')},
                {'title': 'Boudhanath Visit', 'adult_price': Decimal('500'), 'child_price': Decimal('250'), 'duration_hours': Decimal('1.5')},
                {'title': 'Durbar Square Heritage Walk', 'adult_price': Decimal('800'), 'child_price': Decimal('400'), 'duration_hours': Decimal('2.5')},
            ],
            'Dubai': [
                {'title': 'Burj Khalifa Ticket', 'adult_price': Decimal('5000'), 'child_price': Decimal('2500'), 'duration_hours': Decimal('2.0')},
                {'title': 'Desert Safari', 'adult_price': Decimal('4000'), 'child_price': Decimal('2000'), 'duration_hours': Decimal('5.0')},
                {'title': 'Dhow Cruise Dinner', 'adult_price': Decimal('3500'), 'child_price': Decimal('1750'), 'duration_hours': Decimal('3.0')},
                {'title': 'Aquarium Visit', 'adult_price': Decimal('2000'), 'child_price': Decimal('1000'), 'duration_hours': Decimal('2.5')},
            ],
            'Bangkok': [
                {'title': 'Grand Palace Tour', 'adult_price': Decimal('2000'), 'child_price': Decimal('1000'), 'duration_hours': Decimal('3.0')},
                {'title': 'Floating Market', 'adult_price': Decimal('3000'), 'child_price': Decimal('1500'), 'duration_hours': Decimal('4.0')},
                {'title': 'Temple Tour', 'adult_price': Decimal('1500'), 'child_price': Decimal('750'), 'duration_hours': Decimal('3.5')},
                {'title': 'Safari World', 'adult_price': Decimal('5000'), 'child_price': Decimal('2500'), 'duration_hours': Decimal('6.0')},
            ],
            'Delhi': [
                {'title': 'Red Fort & Old City Tour', 'adult_price': Decimal('1500'), 'child_price': Decimal('750'), 'duration_hours': Decimal('4.0')},
                {'title': 'Qutub Minar Tour', 'adult_price': Decimal('1000'), 'child_price': Decimal('500'), 'duration_hours': Decimal('2.0')},
                {'title': 'Taj Mahal Day Trip', 'adult_price': Decimal('5000'), 'child_price': Decimal('2500'), 'duration_hours': Decimal('10.0')},
                {'title': 'Akshardham Visit', 'adult_price': Decimal('1000'), 'child_price': Decimal('500'), 'duration_hours': Decimal('3.0')},
            ],
            'Chitwan': [
                {'title': 'Jeep Safari', 'adult_price': Decimal('3000'), 'child_price': Decimal('1500'), 'duration_hours': Decimal('5.0')},
                {'title': 'Bird Watching', 'adult_price': Decimal('1200'), 'child_price': Decimal('600'), 'duration_hours': Decimal('3.0')},
                {'title': 'Crocodile Breeding Center', 'adult_price': Decimal('500'), 'child_price': Decimal('250'), 'duration_hours': Decimal('1.5')},
                {'title': 'Rapti Rafting', 'adult_price': Decimal('2500'), 'child_price': Decimal('1250'), 'duration_hours': Decimal('3.0')},
            ],
        }

        created_activities = {}
        for dest_name, activity_list in activities_data.items():
            created_activities[dest_name] = []
            if dest_name not in created_destinations:
                continue
            dest = created_destinations[dest_name]
            for act_data in activity_list:
                try:
                    activity, created = Activity.objects.get_or_create(
                        title=act_data['title'],
                        destination=dest,
                        defaults=act_data,
                    )
                    created_activities[dest_name].append(activity)
                    if created:
                        activities_created += 1
                        self.stdout.write(self.style.SUCCESS(f'Created activity: {activity.title}'))
                    else:
                        self.stdout.write(f'Activity already exists: {activity.title}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating activity {act_data["title"]}: {str(e)}'))

        transport_data = {
            'Sauraha': [
                {'vehicle_type': 'BUS', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('1000'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('6.0')},
                {'vehicle_type': 'CAR', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('0'), 'per_vehicle_price': Decimal('7000'), 'duration_hours': Decimal('5.0')},
            ],
            'Chitwan': [
                {'vehicle_type': 'BUS', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('1000'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('6.0')},
                {'vehicle_type': 'CAR', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('0'), 'per_vehicle_price': Decimal('7000'), 'duration_hours': Decimal('5.0')},
                {'vehicle_type': 'FLIGHT', 'route_origin': 'Kathmandu to Bharatpur', 'per_person_price': Decimal('5500'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('0.5')},
            ],
            'Pokhara': [
                {'vehicle_type': 'BUS', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('1200'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('7.0')},
                {'vehicle_type': 'CAR', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('0'), 'per_vehicle_price': Decimal('8000'), 'duration_hours': Decimal('6.0')},
                {'vehicle_type': 'FLIGHT', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('5000'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('0.5')},
            ],
            'Kathmandu': [
                {'vehicle_type': 'CAR', 'route_origin': 'Tribhuvan Airport', 'per_person_price': Decimal('0'), 'per_vehicle_price': Decimal('1500'), 'duration_hours': Decimal('0.5')},
                {'vehicle_type': 'BUS', 'route_origin': 'Ring Road Tour', 'per_person_price': Decimal('300'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('2.0')},
                {'vehicle_type': 'JEEP', 'route_origin': 'Kathmandu Valley Tour', 'per_person_price': Decimal('0'), 'per_vehicle_price': Decimal('5000'), 'duration_hours': Decimal('8.0')},
            ],
            'Dubai': [
                {'vehicle_type': 'FLIGHT', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('50000'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('4.5')},
            ],
            'Bangkok': [
                {'vehicle_type': 'FLIGHT', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('45000'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('3.5')},
            ],
            'Delhi': [
                {'vehicle_type': 'FLIGHT', 'route_origin': 'Kathmandu', 'per_person_price': Decimal('20000'), 'per_vehicle_price': Decimal('0'), 'duration_hours': Decimal('1.5')},
            ],
        }

        for dest_name, transport_list in transport_data.items():
            if dest_name not in created_destinations:
                continue
            dest = created_destinations[dest_name]
            for t_data in transport_list:
                try:
                    transport, created = Transportation.objects.get_or_create(
                        route_origin=t_data['route_origin'],
                        destination=dest,
                        vehicle_type=t_data['vehicle_type'],
                        defaults=t_data,
                    )
                    if created:
                        transports_created += 1
                        self.stdout.write(self.style.SUCCESS(f'Created transport: {transport}'))
                    else:
                        self.stdout.write(f'Transport already exists: {transport}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating transport: {str(e)}'))

        packages_list = [
            {
                'title': 'Chitwan Jungle Safari - 3 Days',
                'destination': 'Chitwan',
                'package_type': 'SINGLE',
                'base_days': 3,
                'base_price': Decimal('15000'),
                'per_day_extra_cost': Decimal('4000'),
                'hotel_category': 'BUDGET',
                'activity_count': 3,
                'is_popular': True,
            },
            {
                'title': 'Pokhara Lakeside Escape - 4 Days',
                'destination': 'Pokhara',
                'package_type': 'COUPLE',
                'base_days': 4,
                'base_price': Decimal('25000'),
                'per_day_extra_cost': Decimal('5000'),
                'hotel_category': 'THREE_STAR',
                'activity_count': 3,
                'is_popular': True,
            },
            {
                'title': 'Kathmandu Heritage Tour - 2 Days',
                'destination': 'Kathmandu',
                'package_type': 'FAMILY',
                'base_days': 2,
                'base_price': Decimal('18000'),
                'per_day_extra_cost': Decimal('3500'),
                'hotel_category': 'BUDGET',
                'activity_count': 3,
                'is_popular': False,
            },
            {
                'title': 'Dubai Luxury Getaway - 5 Days',
                'destination': 'Dubai',
                'package_type': 'COUPLE',
                'base_days': 5,
                'base_price': Decimal('120000'),
                'per_day_extra_cost': Decimal('20000'),
                'hotel_category': 'THREE_STAR',
                'activity_count': 3,
                'is_popular': True,
            },
            {
                'title': 'Bangkok Explorer - 6 Days',
                'destination': 'Bangkok',
                'package_type': 'FAMILY',
                'base_days': 6,
                'base_price': Decimal('85000'),
                'per_day_extra_cost': Decimal('12000'),
                'hotel_category': 'THREE_STAR',
                'activity_count': 3,
                'is_popular': False,
            },
        ]

        for pkg_data in packages_list:
            dest_name = pkg_data['destination']
            if dest_name not in created_destinations:
                continue
            dest = created_destinations[dest_name]
            hotel = None
            if dest_name in created_hotels and pkg_data['hotel_category'] in created_hotels[dest_name]:
                hotel = created_hotels[dest_name][pkg_data['hotel_category']]

            pkg_defaults = {
                'destination': dest,
                'package_type': pkg_data['package_type'],
                'base_days': pkg_data['base_days'],
                'base_price': pkg_data['base_price'],
                'per_day_extra_cost': pkg_data['per_day_extra_cost'],
                'hotel': hotel,
                'is_popular': pkg_data['is_popular'],
                'status': 'Active',
            }
            try:
                package, created = PredefinedPackage.objects.get_or_create(
                    title=pkg_data['title'],
                    defaults=pkg_defaults,
                )
                if created:
                    packages_created += 1
                    pkg_activities = created_activities.get(dest_name, [])[:pkg_data['activity_count']]
                    if pkg_activities:
                        package.included_activities.set(pkg_activities)
                    self.stdout.write(self.style.SUCCESS(f'Created package: {package.title}'))
                else:
                    self.stdout.write(f'Package already exists: {package.title}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating package {pkg_data["title"]}: {str(e)}'))

        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@travelready.com',
                    password='admin123',
                )
                users_created += 1
                self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
            else:
                self.stdout.write('Superuser already exists: admin')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser admin: {str(e)}'))

        try:
            if not User.objects.filter(username='customer').exists():
                User.objects.create_user(
                    username='customer',
                    email='customer@travelready.com',
                    password='customer123',
                )
                users_created += 1
                self.stdout.write(self.style.SUCCESS('Created user: customer'))
            else:
                self.stdout.write('User already exists: customer')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user customer: {str(e)}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('SEED DATA SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Destinations created: {destinations_created}'))
        self.stdout.write(self.style.SUCCESS(f'Hotels created: {hotels_created}'))
        self.stdout.write(self.style.SUCCESS(f'Activities created: {activities_created}'))
        self.stdout.write(self.style.SUCCESS(f'Transports created: {transports_created}'))
        self.stdout.write(self.style.SUCCESS(f'Packages created: {packages_created}'))
        self.stdout.write(self.style.SUCCESS(f'Users created: {users_created}'))
        self.stdout.write(self.style.SUCCESS(f'Seed completed at: {timezone.now()}'))
