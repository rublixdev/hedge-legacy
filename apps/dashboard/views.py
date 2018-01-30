from django.shortcuts import render

from .decorators import verified_user_required


@verified_user_required
def home(request):
    return render(request, 'dashboard/home.html')
