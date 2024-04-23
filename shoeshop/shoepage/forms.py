from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Cash On Delivery')
)

COUNTRY_CHOICES = [
    ('GT', 'Select Country'),
    ('IN', 'India'),
    ('US', 'United States'),
]

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class': 'form-control'
    }))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES,  widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'country-selector'
    }), label='Country')
    state = forms.CharField(required=True, widget=forms.Select(attrs={
        'placeholder': 'Select state',
        'class': 'form-control custom-select d-block w-100',
        'id': 'state-selector'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)
