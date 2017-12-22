from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.account.models import EmailAddress

from .forms import ChangePasswordForm
from .serializers import UserSerializer


@login_required
def profile(request):
    return render(request, 'user/profile.html')


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


class UserCreate(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                EmailAddress.objects.create(user=user, email=user.email, verified=True)
                data = {'id': user.id, 'token': user.auth_token.key}
                return Response(data, status=201)
        else:
            return Response(serializer.errors, status=400)
