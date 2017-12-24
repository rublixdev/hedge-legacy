from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from allauth.account.models import EmailAddress

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
