from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Count, Sum, Q

from .forms import CustomerRegisterForm, DriverRegisterForm, ProfileForm, VehicleForm
from .models import User, Driver, Vehicle
from .decorators import role_required
from rides.models import Ride, Review


def register_choice(request):
    """Landing page asking whether to sign up as customer or driver."""
    return render(request, 'accounts/register_choice.html')


def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_mail(
                subject='Welcome to LocalRide!',
                message=f'Hi {user.first_name}, thanks for joining LocalRide as a rider.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            login(request, user)
            messages.success(request, 'Account created! Welcome to LocalRide.')
            return redirect('accounts:redirect_after_login')
    else:
        form = CustomerRegisterForm()
    return render(request, 'accounts/register_customer.html', {'form': form})


def register_driver(request):
    if request.method == 'POST':
        form = DriverRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_mail(
                subject='Driver Application Received - LocalRide',
                message=f'Hi {user.first_name}, your driver application is under review. '
                        f'We will notify you once approved.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            login(request, user)
            messages.success(request, 'Application submitted! Your account is pending admin approval.')
            return redirect('accounts:redirect_after_login')
    else:
        form = DriverRegisterForm()
    return render(request, 'accounts/register_driver.html', {'form': form})


class LocalRideLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


@login_required
def redirect_after_login(request):
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return redirect('accounts:admin_dashboard')
    elif user.role == 'driver':
        return redirect('accounts:driver_dashboard')
    return redirect('accounts:customer_dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# ---------------------------------------------------------------
# CUSTOMER DASHBOARD
# ---------------------------------------------------------------
@login_required
@role_required('customer')
def customer_dashboard(request):
    rides = Ride.objects.filter(customer=request.user)
    context = {
        'total_rides': rides.count(),
        'completed_rides': rides.filter(status='completed').count(),
        'active_ride': rides.filter(status__in=['requested', 'accepted', 'ongoing']).first(),
        'recent_rides': rides[:5],
        'total_spent': rides.filter(status='completed').aggregate(t=Sum('fare'))['t'] or 0,
    }
    return render(request, 'dashboards/customer_dashboard.html', context)


# ---------------------------------------------------------------
# DRIVER DASHBOARD
# ---------------------------------------------------------------
@login_required
@role_required('driver')
def driver_dashboard(request):
    driver = get_object_or_404(Driver, user=request.user)
    rides = Ride.objects.filter(driver=driver)
    pending_requests = Ride.objects.filter(status='requested', driver__isnull=True) if driver.is_approved else Ride.objects.none()
    context = {
        'driver': driver,
        'vehicle': getattr(driver, 'vehicle', None),
        'pending_requests': pending_requests[:10],
        'active_ride': rides.filter(status__in=['accepted', 'ongoing']).first(),
        'completed_count': rides.filter(status='completed').count(),
        'total_earnings': driver.total_earnings,
        'recent_rides': rides[:5],
        'average_rating': driver.average_rating,
    }
    return render(request, 'dashboards/driver_dashboard.html', context)


@login_required
@role_required('driver')
def driver_vehicle_edit(request):
    driver = get_object_or_404(Driver, user=request.user)
    vehicle = getattr(driver, 'vehicle', None)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            v = form.save(commit=False)
            v.driver = driver
            v.save()
            messages.success(request, 'Vehicle details updated.')
            return redirect('accounts:driver_dashboard')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'accounts/driver_vehicle.html', {'form': form, 'driver': driver})


@login_required
@role_required('driver')
def driver_toggle_status(request):
    driver = get_object_or_404(Driver, user=request.user)
    if not driver.is_approved:
        messages.warning(request, 'Your account is still pending admin approval.')
        return redirect('accounts:driver_dashboard')
    if driver.status == 'available':
        driver.status = 'offline'
    else:
        driver.status = 'available'
    driver.save()
    return redirect('accounts:driver_dashboard')


@login_required
@role_required('driver')
def driver_earnings(request):
    driver = get_object_or_404(Driver, user=request.user)
    rides = Ride.objects.filter(driver=driver, status='completed').select_related('payment')
    return render(request, 'accounts/driver_earnings.html', {'driver': driver, 'rides': rides})


# ---------------------------------------------------------------
# ADMIN DASHBOARD (custom, not Django admin)
# ---------------------------------------------------------------
@login_required
@role_required('admin')
def admin_dashboard(request):
    total_customers = User.objects.filter(role='customer').count()
    total_drivers = Driver.objects.count()
    pending_drivers = Driver.objects.filter(is_approved=False, is_rejected=False).count()
    total_rides = Ride.objects.count()
    completed_rides = Ride.objects.filter(status='completed').count()
    cancelled_rides = Ride.objects.filter(status='cancelled').count()
    total_revenue = Ride.objects.filter(status='completed').aggregate(t=Sum('fare'))['t'] or 0

    rides_by_status = Ride.objects.values('status').annotate(count=Count('id'))
    rides_by_type = Ride.objects.values('ride_type').annotate(count=Count('id'))

    context = {
        'total_customers': total_customers,
        'total_drivers': total_drivers,
        'pending_drivers': pending_drivers,
        'total_rides': total_rides,
        'completed_rides': completed_rides,
        'cancelled_rides': cancelled_rides,
        'total_revenue': total_revenue,
        'rides_by_status': list(rides_by_status),
        'rides_by_type': list(rides_by_type),
        'recent_rides': Ride.objects.select_related('customer', 'driver__user')[:8],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
@role_required('admin')
def manage_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(role='customer')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))
    return render(request, 'admin_panel/manage_users.html', {'users': users, 'query': query})


@login_required
@role_required('admin')
def toggle_user_active(request, user_id):
    user = get_object_or_404(User, id=user_id, role='customer')
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"{user.username}'s account is now {'active' if user.is_active else 'blocked'}.")
    return redirect('accounts:manage_users')


@login_required
@role_required('admin')
def manage_drivers(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    drivers = Driver.objects.select_related('user', 'vehicle')
    if query:
        drivers = drivers.filter(Q(user__username__icontains=query) | Q(license_number__icontains=query))
    if status_filter == 'pending':
        drivers = drivers.filter(is_approved=False, is_rejected=False)
    elif status_filter == 'approved':
        drivers = drivers.filter(is_approved=True)
    elif status_filter == 'rejected':
        drivers = drivers.filter(is_rejected=True)
    return render(request, 'admin_panel/manage_drivers.html', {
        'drivers': drivers, 'query': query, 'status_filter': status_filter,
    })


@login_required
@role_required('admin')
def approve_driver(request, driver_id):
    from django.utils import timezone
    driver = get_object_or_404(Driver, id=driver_id)
    driver.is_approved = True
    driver.is_rejected = False
    driver.approved_at = timezone.now()
    driver.status = 'available'
    driver.save()
    send_mail(
        subject='Your LocalRide driver application was approved!',
        message=f'Hi {driver.user.first_name}, congratulations! You can now start accepting rides.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[driver.user.email],
        fail_silently=True,
    )
    messages.success(request, f'{driver.user.username} approved as a driver.')
    return redirect('accounts:manage_drivers')


@login_required
@role_required('admin')
def reject_driver(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    driver.is_approved = False
    driver.is_rejected = True
    driver.status = 'offline'
    driver.save()
    send_mail(
        subject='Update on your LocalRide driver application',
        message=f'Hi {driver.user.first_name}, unfortunately your driver application was not approved at this time.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[driver.user.email],
        fail_silently=True,
    )
    messages.info(request, f'{driver.user.username} application rejected.')
    return redirect('accounts:manage_drivers')


@login_required
@role_required('admin')
def manage_bookings(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    rides = Ride.objects.select_related('customer', 'driver__user')
    if query:
        rides = rides.filter(
            Q(pickup_address__icontains=query) |
            Q(drop_address__icontains=query) |
            Q(customer__username__icontains=query)
        )
    if status_filter:
        rides = rides.filter(status=status_filter)
    return render(request, 'admin_panel/manage_bookings.html', {
        'rides': rides, 'query': query, 'status_filter': status_filter,
        'status_choices': Ride.STATUS_CHOICES,
    })


@login_required
@role_required('admin')
def reports(request):
    from django.db.models.functions import TruncDate
    daily = (Ride.objects.filter(status='completed')
             .annotate(day=TruncDate('completed_at'))
             .values('day')
             .annotate(rides=Count('id'), revenue=Sum('fare'))
             .order_by('day'))
    top_drivers = Driver.objects.filter(is_approved=True).order_by('-total_earnings')[:5]
    return render(request, 'admin_panel/reports.html', {
        'daily': list(daily), 'top_drivers': top_drivers,
    })
