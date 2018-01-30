from django.conf.urls import url
from allauth.account import views as allauth_views
from . import views


urlpatterns = [
    url(r'^change_password/$', views.change_password),

    # Signup, signin, signout
    url(r"^signup/$", allauth_views.signup, name="account_signup"),
    url(r"^login/$", allauth_views.login, name="account_login"),
    url(r"^logout/$", allauth_views.logout, name="account_logout"),

    # E-mail
    url(r"^confirm-email/$", allauth_views.email_verification_sent,
        name="account_email_verification_sent"),
    url(r'^confirm-phone/$', views.confirm_phone,
        name='confirm_phone_number'),
    url(r"^confirm-email/(?P<key>[-:\w]+)/$", allauth_views.confirm_email,
        name="account_confirm_email"),

    # forgot password
    url(r"^password/reset/$", allauth_views.password_reset,
        name="account_reset_password"),
    url(r"^password/reset/done/$", allauth_views.password_reset_done,
        name="account_reset_password_done"),
    url(r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        allauth_views.password_reset_from_key,
        name="account_reset_password_from_key"),
    url(r"^password/reset/key/done/$", allauth_views.password_reset_from_key_done,
        name="account_reset_password_from_key_done"),
]