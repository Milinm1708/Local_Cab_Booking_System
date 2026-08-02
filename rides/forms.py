from django import forms
from .models import Ride, Review


class BookRideForm(forms.Form):
    pickup_address = forms.CharField(max_length=255)
    pickup_lat = forms.FloatField()
    pickup_lng = forms.FloatField()
    drop_address = forms.CharField(max_length=255)
    drop_lat = forms.FloatField()
    drop_lng = forms.FloatField()
    ride_type = forms.ChoiceField(choices=Ride.RIDE_TYPES)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How was your ride?'}),
        }
