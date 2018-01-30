import random
from os.path import join, dirname, abspath

from django.test import TestCase
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


class BaseTests(TestCase):
    def setUp(self):
        self.bob = self.create_user('bob', 's3cr3t')
        self.alice = self.create_user('alice', 's3cr3t')

    def create_user(self, username, password):
        phone_number = '+1'
        for n in range(12):
            phone_number += str(random.randint(0,9))

        user = User.objects.create_user(username, '%s@example.com' % username, password)
        user.profile.phone_country_code = '1'
        user.profile.phone_number = phone_number
        user.profile.phone_verified = True
        user.profile.save()
        EmailAddress.objects.create(user=user, email=user.email, verified=True)
        return user
