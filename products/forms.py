from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100,
                            required=False, # Search query is optional
                            widget=forms.TextInput(attrs={
                                'class': 'form-control me-2',
                                'placeholder': 'Search products...',
                                'aria-label': 'Search'
                            }))