from hashlib import sha256
from datetime import datetime
import re

from django import forms
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta

from apps.user.models import UserProfile


import random
from django.template.loader import render_to_string
from django.http import HttpResponse



class EnterSMSCode(forms.Form):
    SMS_code = forms.CharField(min_length=6, max_length=6)

    def __init__(self, *args, **kwargs):
        if 'user' not in kwargs:
            raise Exception('The `user` parameter is required for EnterSMSCode.')
        self.user = kwargs.pop('user')
        super(EnterSMSCode, self).__init__(*args, **kwargs)

    def clean_SMS_code(self):
        SMS_code = self.cleaned_data['SMS_code']
        if not re.match(r'^[0-9]+$', SMS_code):
            raise forms.ValidationError('Please enter the 6-digit SMS code sent to your phone.')
        return SMS_code

    

 #   def __init__(self, *args, **kwargs):
 #       if 'user' not in kwargs:
 #           raise Exception('The `user` parameter is required for ChangePasswordForm.')
 #       self.user = kwargs.pop('user')
 #       super(ChangePasswordForm, self).__init__(*args, **kwargs)

#    def clean_current_password(self):
#        value = self.cleaned_data['current_password']
#        if not self.user.check_password(value):
#            raise forms.ValidationError('Please enter the correct password')
#        return value

#    def clean(self):
#        cleaned_data = super(ChangePasswordForm, self).clean()
#        pass1 = cleaned_data.get('new_password')
#        pass2 = cleaned_data.get('confirm_new_password')
#        if pass1 != pass2:
#            self.add_error(
#                'confirm_new_password', 
#                'This value should match with the new password',
#            )
#        return cleaned_data
