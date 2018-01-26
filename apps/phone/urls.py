from django.conf.urls import url
from . import views


urlpatterns = [
    url(r"^enter-verification-code/$", views.enter_verification_code, name="verify_phone"),

]