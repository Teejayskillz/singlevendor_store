# ~/my_ecommerce_project/cart/forms.py

from django import forms

# Ensure PRODUCT_QUANTITY_CHOICES is defined (e.g., up to 100 or whatever you need)
PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 100)] 

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField( # Make sure this is TypedChoiceField
                                choices=PRODUCT_QUANTITY_CHOICES,
                                coerce=int, # <--- THIS LINE IS CRITICAL
                                widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
    override = forms.BooleanField(required=False, widget=forms.HiddenInput)