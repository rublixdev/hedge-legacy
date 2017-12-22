from django import forms
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('name', 'picture', 'bio', 'website')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 2}),
        }

    email = forms.EmailField()
    user = None

    def __init__(self, *args, **kwargs):
        if 'user' not in kwargs:
            raise Exception('The `user` parameter is required for UserProfileForm.')
        self.user = kwargs.pop('user')
        initial = kwargs.setdefault('initial', {})
        initial['email'] = self.user.email
        kwargs['instance'] = self.user.profile
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.user.id).count():
            raise forms.ValidationError('This email is already used by other user.')
        return email

    def save(self):
        super().save()
        self.user.email = self.cleaned_data['email']
        self.user.save()


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Current password',
        min_length=5,
        widget=forms.PasswordInput(),
    )
    new_password = forms.CharField(
        label='New password',
        min_length=5,
        widget=forms.PasswordInput(),
    )
    confirm_new_password = forms.CharField(
        label='Confirm new password',
        min_length=5,
        widget=forms.PasswordInput(),
    )
    user = None

    def __init__(self, *args, **kwargs):
        if 'user' not in kwargs:
            raise Exception('The `user` parameter is required for ChangePasswordForm.')
        self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        value = self.cleaned_data['current_password']
        if not self.user.check_password(value):
            raise forms.ValidationError('Please enter the correct password')
        return value

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        pass1 = cleaned_data.get('new_password')
        pass2 = cleaned_data.get('confirm_new_password')
        if pass1 != pass2:
            self.add_error(
                'confirm_new_password', 
                'This value should match with the new password',
            )
        return cleaned_data
