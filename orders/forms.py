from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email
    
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code:
            raise forms.ValidationError("Postal code is required.")
        return postal_code