from django.conf import settings
from django.db import models
from django.utils import timezone


class Ride(models.Model):
    STATUS_CHOICES = (
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    )
    RIDE_TYPES = (
        ('mini', 'Mini (Hatchback)'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rides_as_customer')
    driver = models.ForeignKey('accounts.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='rides')

    pickup_address = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()

    drop_address = models.CharField(max_length=255)
    drop_lat = models.FloatField()
    drop_lng = models.FloatField()

    ride_type = models.CharField(max_length=10, choices=RIDE_TYPES, default='mini')
    distance_km = models.FloatField(default=0)
    estimated_duration_min = models.FloatField(default=0)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Ride #{self.id} - {self.customer} ({self.status})"

    def mark_status(self, new_status):
        self.status = new_status
        now = timezone.now()
        if new_status == 'accepted':
            self.accepted_at = now
        elif new_status == 'ongoing':
            self.started_at = now
        elif new_status == 'completed':
            self.completed_at = now
        elif new_status == 'cancelled':
            self.cancelled_at = now
        self.save()

    @property
    def has_review(self):
        return hasattr(self, 'review')


class Payment(models.Model):
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('wallet', 'LocalRide Wallet'),
        ('card', 'Card (Demo)'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment #{self.id} for Ride #{self.ride_id} - {self.status}"


class Review(models.Model):
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(default=5)  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review #{self.id} - {self.rating} stars"
