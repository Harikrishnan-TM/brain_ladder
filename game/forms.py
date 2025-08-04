from django import forms
from .models import KYC

class KYCForm(forms.ModelForm):
    class Meta:
        model = KYC
        fields = ['full_name', 'pan_number', 'aadhaar_number']
