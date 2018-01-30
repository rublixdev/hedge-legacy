from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def verified_user_required(f):
    @wraps(f)
    @login_required
    def func(request, *args, **kwargs):
        user = request.user
        if not user.emailaddress_set.first().verified:
            return redirect(reverse('account_email_verification_sent'))
        elif not user.profile.phone_verified:
            return redirect('%s?h=%s' % (
                reverse('confirm_phone_number'),
                user.profile.phone_number_hash,
            ))
        else:
            return f(request, *args, **kwargs)
    return func
