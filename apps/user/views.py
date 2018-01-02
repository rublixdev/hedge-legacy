from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.dispatch import receiver
from django.conf import settings
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
import requests

from .forms import ChangePasswordForm


@login_required
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


@receiver(email_confirmed)
def subscribe_to_mailchimp(sender, email_address, **kwargs):
    try:
        api_key = settings.MAILCHIMP_API_KEY
        list_id = settings.MAILCHIMP_LIST_ID
        url = 'https://us6.api.mailchimp.com/3.0/lists/%s/members' % list_id
        r = requests.post(url, auth=('user', api_key), json={
            'email_address': email_address.email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': email_address.user.profile.name,
                'LNAME': '',
            }            
        })
    except Exception as e:
        print('Something went wrong: %s' % e)
