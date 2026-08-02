from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/driver/', views.register_driver, name='register_driver'),
    path('login/', views.LocalRideLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.redirect_after_login, name='redirect_after_login'),
    path('profile/', views.profile_view, name='profile'),

    # Customer
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),

    # Driver
    path('dashboard/driver/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/vehicle/', views.driver_vehicle_edit, name='driver_vehicle_edit'),
    path('driver/toggle-status/', views.driver_toggle_status, name='driver_toggle_status'),
    path('driver/earnings/', views.driver_earnings, name='driver_earnings'),

    # Admin
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.manage_users, name='manage_users'),
    path('admin-panel/users/<int:user_id>/toggle/', views.toggle_user_active, name='toggle_user_active'),
    path('admin-panel/drivers/', views.manage_drivers, name='manage_drivers'),
    path('admin-panel/drivers/<int:driver_id>/approve/', views.approve_driver, name='approve_driver'),
    path('admin-panel/drivers/<int:driver_id>/reject/', views.reject_driver, name='reject_driver'),
    path('admin-panel/bookings/', views.manage_bookings, name='manage_bookings'),
    path('admin-panel/reports/', views.reports, name='reports'),
]
