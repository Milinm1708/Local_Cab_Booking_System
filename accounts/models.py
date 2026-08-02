from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model shared by all three roles: customer, driver, admin.
    Role decides which dashboard & permissions a user gets.
    """
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_joined_display = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def avatar_url(self):
        if self.profile_photo:
            return self.profile_photo.url
        return None


class Driver(models.Model):
    """Extra profile data for users with role='driver'."""
    STATUS_CHOICES = (
        ('offline', 'Offline'),
        ('available', 'Available'),
        ('busy', 'On a Ride'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=40, unique=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Driver: {self.user.get_full_name() or self.user.username}"

    @property
    def average_rating(self):
        from rides.models import Review
        reviews = Review.objects.filter(ride__driver=self)
        if not reviews.exists():
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def total_rides(self):
        return self.rides.filter(status='completed').count()


class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ('mini', 'Mini (Hatchback)'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
    )
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE, related_name='vehicle')
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='mini')
    make_model = models.CharField(max_length=100, help_text="e.g. Maruti Swift")
    color = models.CharField(max_length=40)
    plate_number = models.CharField(max_length=20, unique=True)
    year = models.PositiveSmallIntegerField(default=2020)
    seats = models.PositiveSmallIntegerField(default=4)

    def __str__(self):
        return f"{self.make_model} ({self.plate_number})"
