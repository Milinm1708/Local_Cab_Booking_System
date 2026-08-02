from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect

from .models import ContactMessage


def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and email and subject and message):
            messages.error(request, 'Please fill in all fields.')
        else:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            send_mail(
                subject=f'[LocalRide Contact] {subject}',
                message=f'From: {name} <{email}>\n\n{message}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['support@localride.example.com'],
                fail_silently=True,
            )
            messages.success(request, "Thanks! We've received your message and will get back to you soon.")
            return redirect('core:contact')
    return render(request, 'core/contact.html')
