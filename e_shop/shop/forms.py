from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Ratting, Order
 
class RegistrationForm(UserCreationForm):
     email = forms.EmailField(required=True)
     first_name=forms.CharField( required=True),
     last_name=forms.CharField(required=True),
     class Meta:
            model = User
            fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Ratting
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'rows': 4}),    
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4}),
        }
 
  
