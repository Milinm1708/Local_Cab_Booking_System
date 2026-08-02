"""
Management command to populate LocalRide with realistic sample/test data.

Usage:
    python manage.py seed_data
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, Driver, Vehicle
from rides.models import Ride, Payment, Review
from rides.utils import haversine_km, estimate_fare
from core.models import ContactMessage


PUNE_LANDMARKS = [
    ("Koregaon Park", 18.5362, 73.8938),
    ("Pune Railway Station", 18.5286, 73.8744),
    ("Shivaji Nagar", 18.5308, 73.8474),
    ("Hinjewadi IT Park", 18.5913, 73.7389),
    ("Viman Nagar", 18.5679, 73.9143),
    ("Pune Airport", 18.5822, 73.9197),
    ("Kothrud", 18.5074, 73.8077),
    ("Baner", 18.5590, 73.7868),
    ("Camp Area", 18.5122, 73.8797),
    ("Hadapsar", 18.5089, 73.9260),
    ("Aundh", 18.5590, 73.8077),
    ("Magarpatta City", 18.5158, 73.9280),
]


class Command(BaseCommand):
    help = "Seed the database with sample users, drivers, vehicles and rides for testing."

    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write(self.style.WARNING("Seeding LocalRide sample data..."))

        # ---------------- Admin ----------------
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@localride.example.com', password='admin123',
                first_name='Ava', last_name='Admin',
            )
            admin.role = 'admin'
            admin.phone = '9999900000'
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin: admin / admin123"))

        # ---------------- Riders ----------------
        rider_names = [
            ("rider1", "Aditi", "Sharma"), ("rider2", "Rohan", "Verma"),
            ("rider3", "Meera", "Iyer"), ("rider4", "Karan", "Shah"),
            ("rider5", "Priya", "Nair"),
        ]
        riders = []
        for uname, fname, lname in rider_names:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    email=f"{uname}@example.com", first_name=fname, last_name=lname,
                    role='customer', phone=f"98{random.randint(10000000,99999999)}",
                ),
            )
            if created:
                user.set_password('rider12345')
                user.save()
            riders.append(user)
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(riders)} rider accounts (password: rider12345)"))

        # ---------------- Drivers ----------------
        driver_data = [
            ("driver1", "Suresh", "Patil", "MH12AB1234", "mini", "Maruti Swift", "White", 2019, True),
            ("driver2", "Ramesh", "Kulkarni", "MH14CD5678", "sedan", "Honda City", "Silver", 2021, True),
            ("driver3", "Vikram", "Deshmukh", "MH12EF9012", "suv", "Toyota Innova", "Black", 2020, True),
            ("driver4", "Anil", "Joshi", "MH14GH3456", "mini", "Hyundai i10", "Red", 2018, False),
            ("driver5", "Sanjay", "More", "MH12IJ7890", "sedan", "Skoda Rapid", "Blue", 2022, False),
        ]
        drivers = []
        for uname, fname, lname, license_no, vtype, model, color, year, approved in driver_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults=dict(
                    email=f"{uname}@example.com", first_name=fname, last_name=lname,
                    role='driver', phone=f"97{random.randint(10000000,99999999)}",
                ),
            )
            if created:
                user.set_password('driver12345')
                user.save()
            driver, _ = Driver.objects.get_or_create(
                user=user,
                defaults=dict(
                    license_number=license_no, experience_years=random.randint(2, 12),
                    is_approved=approved, status='available' if approved else 'offline',
                    approved_at=timezone.now() if approved else None,
                ),
            )
            Vehicle.objects.get_or_create(
                driver=driver,
                defaults=dict(
                    vehicle_type=vtype, make_model=model, color=color,
                    plate_number=license_no, year=year, seats=4 if vtype != 'suv' else 6,
                ),
            )
            drivers.append(driver)
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(drivers)} driver accounts (password: driver12345)"))

        approved_drivers = [d for d in drivers if d.is_approved]

        # ---------------- Rides ----------------
        if Ride.objects.count() < 15:
            statuses_pool = ['completed'] * 8 + ['cancelled'] * 2 + ['requested'] * 2 + ['accepted', 'ongoing']
            for i in range(15):
                pickup = random.choice(PUNE_LANDMARKS)
                drop = random.choice([l for l in PUNE_LANDMARKS if l != pickup])
                ride_type = random.choice(['mini', 'sedan', 'suv'])
                distance = haversine_km(pickup[1], pickup[2], drop[1], drop[2])
                fare, duration = estimate_fare(distance, ride_type)
                status = statuses_pool[i % len(statuses_pool)]
                driver = random.choice(approved_drivers) if status != 'requested' and approved_drivers else None

                requested_at = timezone.now() - timedelta(days=random.randint(0, 20), hours=random.randint(0, 23))
                ride = Ride.objects.create(
                    customer=random.choice(riders),
                    driver=driver,
                    pickup_address=f"{pickup[0]}, Pune", pickup_lat=pickup[1], pickup_lng=pickup[2],
                    drop_address=f"{drop[0]}, Pune", drop_lat=drop[1], drop_lng=drop[2],
                    ride_type=ride_type, distance_km=round(distance, 2),
                    estimated_duration_min=duration, fare=fare, status=status,
                )
                Ride.objects.filter(id=ride.id).update(requested_at=requested_at)
                ride.refresh_from_db()

                if status in ['accepted', 'ongoing', 'completed']:
                    ride.accepted_at = requested_at + timedelta(minutes=3)
                if status in ['ongoing', 'completed']:
                    ride.started_at = requested_at + timedelta(minutes=8)
                if status == 'completed':
                    ride.completed_at = requested_at + timedelta(minutes=int(duration) + 8)
                if status == 'cancelled':
                    ride.cancelled_at = requested_at + timedelta(minutes=2)
                    ride.cancel_reason = 'Changed my plans'
                ride.save()

                payment_status = 'paid' if status == 'completed' else 'pending'
                Payment.objects.get_or_create(
                    ride=ride, defaults=dict(
                        amount=fare, method=random.choice(['cash', 'wallet', 'card']),
                        status=payment_status,
                        paid_at=ride.completed_at if status == 'completed' else None,
                    ),
                )

                if status == 'completed' and driver:
                    driver.total_earnings += fare
                    driver.save()
                    if random.random() > 0.3:
                        Review.objects.get_or_create(
                            ride=ride, defaults=dict(
                                rating=random.randint(3, 5),
                                comment=random.choice([
                                    'Smooth ride, thanks!', 'Driver was polite and on time.',
                                    'Great experience overall.', 'Clean car, safe driving.', '',
                                ]),
                            ),
                        )
            self.stdout.write(self.style.SUCCESS("Created 15 sample rides with payments & reviews"))

        # ---------------- Contact messages ----------------
        if ContactMessage.objects.count() == 0:
            ContactMessage.objects.create(
                name='Sample User', email='sample@example.com', subject='Great platform!',
                message='Just wanted to say the booking experience was smooth. Keep it up!',
            )
            self.stdout.write(self.style.SUCCESS("Added a sample contact message"))

        self.stdout.write(self.style.SUCCESS("\n✅ Seeding complete!"))
        self.stdout.write("Login credentials:")
        self.stdout.write("  Admin  -> admin / admin123")
        self.stdout.write("  Rider  -> rider1 / rider12345 (also rider2..rider5)")
        self.stdout.write("  Driver -> driver1 / driver12345 (also driver2..driver5; driver4/5 pending approval)")
