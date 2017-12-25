from hashlib import sha256
from datetime import datetime
import re

from django import forms
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

from .models import UserProfile


class SignupForm(forms.Form):
    name = forms.CharField(min_length=6, max_length=150)
    phone_number = forms.CharField(min_length=12, max_length=25)
    wallet_address = forms.CharField()
    date_of_birth = forms.DateField()
    terms = forms.BooleanField()

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^[0-9\- ()]+$', phone_number):
            raise forms.ValidationError('Only numbers, spaces, hyphens, and parentheses allowed.')
        return phone_number

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        diff = relativedelta(datetime.now(), dob)
        if diff.years < 33:
            raise forms.ValidationError('You have to be 33 years old or older.')
        return dob

    def clean_wallet_address(self):
        def decode_base58(bc, length):
            digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
            n = 0
            for char in bc:
                n = n * 58 + digits58.index(char)
            return n.to_bytes(length, 'big')

        address = self.cleaned_data['wallet_address']
        try:
            bcbytes = decode_base58(address, 25)
            if bcbytes[-4:] != sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]:
                raise ValueError()
        except Exception:
            raise forms.ValidationError('Invalid wallet address.')
        return address

    def signup(self, request, user):
        user.profile.name = self.cleaned_data['name']
        user.profile.phone_number = self.cleaned_data['phone_number']
        user.profile.wallet_address = self.cleaned_data['wallet_address']
        user.profile.date_of_birth = self.cleaned_data['date_of_birth']
        user.profile.save()


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Current password',
        min_length=5,
        widget=forms.PasswordInput(),
    )
    new_password = forms.CharField(
        label='New password',
        min_length=5,
        widget=forms.PasswordInput(),
    )
    confirm_new_password = forms.CharField(
        label='Confirm new password',
        min_length=5,
        widget=forms.PasswordInput(),
    )
    user = None

    def __init__(self, *args, **kwargs):
        if 'user' not in kwargs:
            raise Exception('The `user` parameter is required for ChangePasswordForm.')
        self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        value = self.cleaned_data['current_password']
        if not self.user.check_password(value):
            raise forms.ValidationError('Please enter the correct password')
        return value

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        pass1 = cleaned_data.get('new_password')
        pass2 = cleaned_data.get('confirm_new_password')
        if pass1 != pass2:
            self.add_error(
                'confirm_new_password', 
                'This value should match with the new password',
            )
        return cleaned_data
