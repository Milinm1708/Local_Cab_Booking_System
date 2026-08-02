from django.urls import path
from . import views

app_name = 'rides'

urlpatterns = [
    path('book/', views.book_ride, name='book_ride'),
    path('fare-estimate/', views.fare_estimate_api, name='fare_estimate_api'),
    path('history/', views.ride_history, name='ride_history'),
    path('<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('<int:ride_id>/cancel/', views.cancel_ride, name='cancel_ride'),
    path('<int:ride_id>/review/', views.submit_review, name='submit_review'),

    # Driver actions
    path('<int:ride_id>/accept/', views.accept_ride, name='accept_ride'),
    path('<int:ride_id>/reject/', views.reject_ride, name='reject_ride'),
    path('<int:ride_id>/start/', views.start_ride, name='start_ride'),
    path('<int:ride_id>/complete/', views.complete_ride, name='complete_ride'),
]
