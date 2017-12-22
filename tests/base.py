from os.path import join, dirname, abspath

from django.test import TestCase
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress


class BaseTests(TestCase):
    def setUp(self):
        self.bob = self.create_user('bob', 's3cr3t')
        self.alice = self.create_user('alice', 's3cr3t')

    def create_user(self, username, password):
        user = User.objects.create_user(username, '%s@example.com' % username, password)
        EmailAddress.objects.create(user=user, email=user.email, verified=True)
        return user
