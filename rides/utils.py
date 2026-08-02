import math
from django.conf import settings


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points, in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def estimate_fare(distance_km, ride_type='mini', avg_speed_kmh=28.0):
    """
    Simple transparent fare model (no external pricing API needed):
    fare = (base + per_km*distance + per_min*duration) * type_multiplier
    """
    duration_min = (distance_km / avg_speed_kmh) * 60 if avg_speed_kmh else 0
    multiplier = settings.FARE_MULTIPLIERS.get(ride_type, 1.0)
    fare = (settings.FARE_BASE + settings.FARE_PER_KM * distance_km + settings.FARE_PER_MIN * duration_min) * multiplier
    return round(fare, 2), round(duration_min, 1)
