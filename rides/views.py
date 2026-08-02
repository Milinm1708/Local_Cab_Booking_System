import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import Driver
from .models import Ride, Payment, Review
from .forms import ReviewForm
from .utils import haversine_km, estimate_fare


@login_required
@role_required('customer')
def book_ride(request):
    if request.method == 'POST':
        pickup_address = request.POST.get('pickup_address')
        pickup_lat = float(request.POST.get('pickup_lat'))
        pickup_lng = float(request.POST.get('pickup_lng'))
        drop_address = request.POST.get('drop_address')
        drop_lat = float(request.POST.get('drop_lat'))
        drop_lng = float(request.POST.get('drop_lng'))
        ride_type = request.POST.get('ride_type', 'mini')

        distance = haversine_km(pickup_lat, pickup_lng, drop_lat, drop_lng)
        fare, duration = estimate_fare(distance, ride_type)

        ride = Ride.objects.create(
            customer=request.user,
            pickup_address=pickup_address, pickup_lat=pickup_lat, pickup_lng=pickup_lng,
            drop_address=drop_address, drop_lat=drop_lat, drop_lng=drop_lng,
            ride_type=ride_type, distance_km=round(distance, 2),
            estimated_duration_min=duration, fare=fare,
        )
        Payment.objects.create(ride=ride, amount=fare, method='cash', status='pending')

        send_mail(
            subject='Ride booked - LocalRide',
            message=f'Your ride from {pickup_address} to {drop_address} has been requested. '
                    f'Estimated fare: Rs {fare}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email] if request.user.email else [],
            fail_silently=True,
        )
        messages.success(request, 'Ride requested! Looking for a nearby driver...')
        return redirect('rides:ride_detail', ride_id=ride.id)

    return render(request, 'rides/book_ride.html')


@require_POST
@login_required
def fare_estimate_api(request):
    """AJAX endpoint: returns live fare estimate as the user picks locations/vehicle."""
    try:
        data = json.loads(request.body)
        pickup_lat = float(data['pickup_lat'])
        pickup_lng = float(data['pickup_lng'])
        drop_lat = float(data['drop_lat'])
        drop_lng = float(data['drop_lng'])
        ride_type = data.get('ride_type', 'mini')
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid input'}, status=400)

    distance = haversine_km(pickup_lat, pickup_lng, drop_lat, drop_lng)
    estimates = {}
    for rtype in ['mini', 'sedan', 'suv']:
        fare, duration = estimate_fare(distance, rtype)
        estimates[rtype] = {'fare': fare, 'duration': duration}

    return JsonResponse({
        'distance_km': round(distance, 2),
        'estimates': estimates,
    })


@login_required
def ride_detail(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    if request.user != ride.customer and (not hasattr(request.user, 'driver_profile') or ride.driver_id != request.user.driver_profile.id) and request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, 'You cannot view this ride.')
        return redirect('core:home')

    review_form = None
    if request.user == ride.customer and ride.status == 'completed' and not ride.has_review:
        review_form = ReviewForm(initial={'rating': 5})

    return render(request, 'rides/ride_detail.html', {'ride': ride, 'review_form': review_form})


@login_required
@role_required('customer')
def ride_history(request):
    rides = Ride.objects.filter(customer=request.user)
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')
    if status_filter:
        rides = rides.filter(status=status_filter)
    if query:
        rides = rides.filter(pickup_address__icontains=query) | rides.filter(drop_address__icontains=query)
    return render(request, 'rides/ride_history.html', {
        'rides': rides, 'status_filter': status_filter, 'query': query,
    })


@login_required
@role_required('customer')
def cancel_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, customer=request.user)
    if ride.status in ['requested', 'accepted']:
        ride.mark_status('cancelled')
        ride.cancel_reason = request.POST.get('reason', 'Cancelled by customer')
        ride.save()
        if ride.driver:
            ride.driver.status = 'available'
            ride.driver.save()
        messages.success(request, 'Ride cancelled.')
    else:
        messages.error(request, 'This ride can no longer be cancelled.')
    return redirect('rides:ride_history')


@login_required
@role_required('customer')
def submit_review(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, customer=request.user, status='completed')
    if request.method == 'POST' and not ride.has_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ride = ride
            review.save()
            messages.success(request, 'Thanks for your feedback!')
    return redirect('rides:ride_detail', ride_id=ride.id)


# ---------------------------------------------------------------
# DRIVER-SIDE RIDE MANAGEMENT
# ---------------------------------------------------------------
@login_required
@role_required('driver')
def accept_ride(request, ride_id):
    driver = get_object_or_404(Driver, user=request.user)
    if not driver.is_approved:
        messages.error(request, 'Your account is not yet approved.')
        return redirect('accounts:driver_dashboard')
    ride = get_object_or_404(Ride, id=ride_id, status='requested', driver__isnull=True)
    ride.driver = driver
    ride.mark_status('accepted')
    driver.status = 'busy'
    driver.save()
    send_mail(
        subject='Driver assigned - LocalRide',
        message=f'{driver.user.get_full_name() or driver.user.username} has accepted your ride request.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ride.customer.email] if ride.customer.email else [],
        fail_silently=True,
    )
    messages.success(request, 'Ride accepted! Head to the pickup point.')
    return redirect('rides:ride_detail', ride_id=ride.id)


@login_required
@role_required('driver')
def reject_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, status='requested')
    messages.info(request, 'Ride request skipped.')
    return redirect('accounts:driver_dashboard')


@login_required
@role_required('driver')
def start_ride(request, ride_id):
    driver = get_object_or_404(Driver, user=request.user)
    ride = get_object_or_404(Ride, id=ride_id, driver=driver, status='accepted')
    ride.mark_status('ongoing')
    messages.success(request, 'Ride started. Drive safe!')
    return redirect('rides:ride_detail', ride_id=ride.id)


@login_required
@role_required('driver')
def complete_ride(request, ride_id):
    driver = get_object_or_404(Driver, user=request.user)
    ride = get_object_or_404(Ride, id=ride_id, driver=driver, status='ongoing')
    ride.mark_status('completed')

    payment = getattr(ride, 'payment', None)
    if payment:
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save()

    driver.total_earnings += ride.fare
    driver.status = 'available'
    driver.save()

    messages.success(request, f'Ride completed! Rs {ride.fare} added to your earnings.')
    return redirect('accounts:driver_dashboard')
