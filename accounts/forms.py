from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Driver, Vehicle


class CustomerRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class DriverRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    license_number = forms.CharField(max_length=40, required=True)
    experience_years = forms.IntegerField(min_value=0, required=True)
    vehicle_type = forms.ChoiceField(choices=Vehicle.VEHICLE_TYPES)
    make_model = forms.CharField(max_length=100, required=True)
    color = forms.CharField(max_length=40, required=True)
    plate_number = forms.CharField(max_length=20, required=True)
    year = forms.IntegerField(min_value=1990, max_value=2030, required=True)
    seats = forms.IntegerField(min_value=2, max_value=8, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'driver'
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            driver = Driver.objects.create(
                user=user,
                license_number=self.cleaned_data['license_number'],
                experience_years=self.cleaned_data['experience_years'],
            )
            Vehicle.objects.create(
                driver=driver,
                vehicle_type=self.cleaned_data['vehicle_type'],
                make_model=self.cleaned_data['make_model'],
                color=self.cleaned_data['color'],
                plate_number=self.cleaned_data['plate_number'],
                year=self.cleaned_data['year'],
                seats=self.cleaned_data['seats'],
            )
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'profile_photo']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'make_model', 'color', 'plate_number', 'year', 'seats']
