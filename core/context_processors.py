"""Global template context: makes role helpers & site meta available everywhere."""


def site_context(request):
    user = getattr(request, 'user', None)
    ctx = {
        'SITE_NAME': 'LocalRide',
        'is_customer': False,
        'is_driver': False,
        'is_admin_role': False,
    }
    if user and user.is_authenticated:
        ctx['is_customer'] = user.role == 'customer'
        ctx['is_driver'] = user.role == 'driver'
        ctx['is_admin_role'] = user.role == 'admin' or user.is_superuser
    return ctx
