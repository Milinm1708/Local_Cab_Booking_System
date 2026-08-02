from django.contrib import admin
from .models import Ride, Payment, Review


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'driver', 'status', 'ride_type', 'fare', 'requested_at')
    list_filter = ('status', 'ride_type')
    search_fields = ('pickup_address', 'drop_address', 'customer__username')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'amount', 'method', 'status', 'paid_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'rating', 'created_at')
