from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.dispatch import receiver
from django.conf import settings
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
import requests

from apps.dashboard.decorators import verified_user_required
from .models import UserProfile
from .forms import ChangePasswordForm


@verified_user_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(
                request,
                'Password successfully changed.',
                extra_tags='app',
            )
            return redirect(request.path)
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'user/change_password.html', {'form': form})


def confirm_phone(request):
    profile = get_object_or_404(UserProfile, phone_number_hash=request.GET.get('h'))
    if profile.phone_verified:
        return redirect(request, '/')

    error = None
    if request.method == 'POST':
        try:
            url = 'https://api.authy.com/protected/json/phones/verification/check'
            payload = {
                'api_key': settings.TWILIO_API_KEY,
                'country_code': profile.phone_country_code,
                'phone_number': profile.phone_number,
                'verification_code': request.POST.get('verification_code'),
            }
            r = requests.get(url, params=payload)
            if r.status_code == 200:
                profile.phone_verified = True
                profile.save()
                return redirect('/')
            else:
                error = 'Incorrect verification code.'
        except Exception as e:
            print(e)
            return HttpResponseServerError()
    else:
        try:
            url = 'https://api.authy.com/protected/json/phones/verification/start' \
                  '?api_key=%s' % settings.TWILIO_API_KEY
            payload = {
                'via': 'sms',                
                'country_code': profile.phone_country_code,
                'phone_number': profile.phone_number,
            }
            r = requests.post(url, data=payload)
        except Exception as e:
            print(e)
            return HttpResponseServerError()

    return render(request, 'user/confirm_phone.html', {
        'user': profile.user,
        'error': error,
    })


@receiver(email_confirmed)
def subscribe_to_mailchimp(sender, email_address, **kwargs):
    user = email_address.user
    try:
        api_key = settings.MAILCHIMP_API_KEY
        list_id = settings.MAILCHIMP_LIST_ID
        url = 'https://us6.api.mailchimp.com/3.0/lists/%s/members' % list_id
        r = requests.post(url, auth=('user', api_key), json={
            'email_address': email_address.email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': user.profile.first_name,
                'LNAME': user.profile.last_name,
            }            
        })
    except Exception as e:
        print('Something went wrong: %s' % e)
