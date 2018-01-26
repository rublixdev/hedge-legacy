from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from apps.phone.forms import EnterSMSCode
from apps.user.forms import SignupForm


def home(request):

	if request.user.is_authenticated():
		#print (request.user.profile.phone_number)
		if request.user.profile.phone_authenticated == False:
			return redirect('verify_phone')
		else:
			return render(request, "dashboard/home.html")
	
	else:
		return redirect('account_signup')
