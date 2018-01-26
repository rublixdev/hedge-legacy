from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib import messages
from django.dispatch import receiver
from django.conf import settings

import requests

from .forms import EnterSMSCode
from .models import send_phone_verification_code


#@login_required
def enter_verification_code(request):
    if request.method == 'POST':
        
        form = EnterSMSCode(request.POST, user=request.user)
        
        if form.is_valid():
            
            user_input = form.cleaned_data['SMS_code']
           

            if int(user_input) == int(request.user.profile.SMS_activation_code):
                request.user.profile.phone_authenticated = True
                request.user.profile.save()
                return redirect('/dashboard/')
            else:
                #send_phone_verification_code(user = request.user)
                form = EnterSMSCode(user=request.user)
                return render(request, 'phone/enter_resent_verification_code.html', {'form': form})

            #new_password = form.cleaned_data['new_password']
            #request.user.set_password(new_password)
            #request.user.save()
            #update_session_auth_hash(request, request.user)
            #messages.success(
            #    request,
            #    'Password successfully changed.',
            #    extra_tags='app',
            #)
            return redirect(request.path)
    else:
        send_phone_verification_code(user = request.user)
        form = EnterSMSCode(user=request.user)

    return render(request, 'phone/enter_verification_code.html', {'form': form})


