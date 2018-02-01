import os

from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash, login
from django.contrib import messages
from django.dispatch import receiver
from django.conf import settings
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
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


def facebook_login(request):
    client_id = settings.FB_OAUTH_CLIENT_ID
    client_secret = settings.FB_OAUTH_CLIENT_SECRET
    authorization_base_url = 'https://www.facebook.com/dialog/oauth'
    token_url = 'https://graph.facebook.com/oauth/access_token'
    redirect_uri = 'http://localhost:3000/user/facebook-login'

    if settings.DEBUG:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    try:
        oauth_state = request.session['oauth_state']
        del request.session['oauth_state']
    except KeyError:
        oauth_state = None

    facebook = OAuth2Session(client_id, scope='email',
                             redirect_uri=redirect_uri, state=oauth_state)
    facebook = facebook_compliance_fix(facebook)

    if request.GET.get('error') == 'access_denied':
        return redirect('/user/login/')
    elif not request.GET.get('code'):
        authorization_url, state = facebook.authorization_url(authorization_base_url)
        request.session['oauth_state'] = state
        return redirect(authorization_url)
    else:
        facebook.fetch_token(token_url, client_secret=client_secret,
                             authorization_response=request.build_absolute_uri())

    r = facebook.get('https://graph.facebook.com/me?fields=first_name,last_name,email')
    data = r.json()

    try:
        profile = UserProfile.objects.get(facebook_user_id=data.get('id'))
        login(request, profile.user, 
              backend='allauth.account.auth_backends.AuthenticationBackend')
        return redirect('/')
    except UserProfile.DoesNotExist:
        pass

    return render(request, 'account/signup.html', {
        'facebook_user_id': data.get('id'),
        'first_name': data.get('first_name'), 
        'last_name': data.get('last_name'), 
        'email': data.get('email'), 
        'date_of_birth': data.get('birthday'),
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
