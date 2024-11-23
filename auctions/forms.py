from django import forms
from django.forms import ModelForm
from .models import Listing, Comment

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
            }),
            'start_price': forms.NumberInput(attrs = {
                'class': 'form-control'
            }),
            'image_url': forms.URLInput(attrs = {
                'class': 'form-control'
            }),
            'category': forms.Select(attrs = {
                'class': 'form-control'
            })
        
        }

class EditCommentForm(forms.Form):
    listing_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter your comment here', 'class': 'form-control'})
    )

