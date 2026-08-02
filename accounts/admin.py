from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Driver, Vehicle


@admin.register(User)
class LocalRideUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('LocalRide Info', {'fields': ('role', 'phone', 'address', 'profile_photo')}),
    )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'status', 'is_approved', 'total_earnings')
    list_filter = ('status', 'is_approved')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('driver', 'vehicle_type', 'make_model', 'plate_number')
