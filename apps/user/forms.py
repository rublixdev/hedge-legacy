from hashlib import sha256
from datetime import datetime
import re

from django import forms
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

from .models import UserProfile


class SignupForm(forms.Form):
    first_name = forms.CharField(min_length=2, max_length=50)
    last_name = forms.CharField(min_length=2, max_length=50)
    phone_country_code = forms.CharField(required=False)
    phone_number = forms.CharField(min_length=11, max_length=25)
    wallet_address = forms.CharField()
    date_of_birth = forms.DateField()
    facebook_user_id = forms.CharField(required=False)
    terms = forms.BooleanField()

    def clean_phone_country_code(self):
        cc = self.cleaned_data['phone_country_code']
        if not re.match(r'[0-9]{1,5}$', cc):
            raise forms.ValidationError('Please select the country code.')
        return cc

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+[0-9\- ()]+$', phone_number):
            raise forms.ValidationError('Only numbers, spaces, hyphens, and parentheses allowed.')
        elif UserProfile.objects.filter(phone_number=phone_number).count():
            raise forms.ValidationError('A user is already registered with this phone number.')
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
            # Bitcoin address
            bcbytes = decode_base58(address, 25)
            if bcbytes[-4:] != sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]:
                raise ValueError()
        except Exception:
            # Ethereum address
            if not re.match(r'^(0x)?[0-9a-f]{40}$', address, flags=re.I):
                raise forms.ValidationError('Invalid wallet address.')
        return address

    def clean_facebook_user_id(self):
        uid = self.cleaned_data['facebook_user_id']
        if uid and UserProfile.objects.filter(facebook_user_id=uid).count():
            raise forms.ValidationError('A user is already registered with this Facebook ID.')
        return uid

    def signup(self, request, user):
        user.profile.first_name = self.cleaned_data['first_name']
        user.profile.last_name = self.cleaned_data['last_name']
        user.profile.phone_country_code = self.cleaned_data['phone_country_code']
        user.profile.phone_number = self.cleaned_data['phone_number']
        user.profile.wallet_address = self.cleaned_data['wallet_address']
        user.profile.date_of_birth = self.cleaned_data['date_of_birth']
        user.profile.facebook_user_id = self.cleaned_data['facebook_user_id']
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
