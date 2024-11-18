from django import forms
from django.forms import ModelForm
from .models import Listing

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "desc", "start_price", "image_url", "category"]

        widgets = {
            'title': forms.TextInput(attrs = {
                'class': 'form-control',            
            }),
            'desc': forms.Textarea(attrs = {
                'class': 'form-control'
        })
        }

