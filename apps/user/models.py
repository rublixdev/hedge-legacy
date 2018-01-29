import hashlib
from urllib.parse import urlencode

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        related_name='profile',
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=25,
        blank=True,
        null=True,
    )
    wallet_address = models.CharField(
        max_length=55,
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )
    picture = models.ImageField(
        blank=True, 
        null=True, 
        upload_to='profile_pictures',
    )
    bio = models.TextField(
        max_length=250, 
        blank=True, 
        null=True,
    )
    SMS_activation_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
    )
    phone_authenticated = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def gravatar_url(self):
        url = 'https://www.gravatar.com/avatar/%s?%s' % (
            hashlib.md5(self.user.email.lower().encode('utf-8')).hexdigest(),
            urlencode(dict(s=30)),
        )
        return url

    def picture_url(self):
        if self.picture:
            return self.picture.url
        else:
            return self.gravatar_url


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
