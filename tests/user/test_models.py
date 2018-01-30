import hashlib

from django.contrib.auth.models import User

from apps.user.models import UserProfile
from ..base import BaseTests


class UserProfileTests(BaseTests):
    def test_create_phone_number_hash_on_save(self):
        user = User.objects.create_user('user1', 'user1@example.com', 's3cr3t')
        user.profile.phone_country_code = '1'
        user.profile.phone_number = '+11234567890'
        user.profile.save()

        expected_hash = hashlib.md5('+11234567890'.encode('utf-8')).hexdigest()

        user.profile.refresh_from_db()
        self.assertEqual(user.profile.phone_number_hash, expected_hash)
        self.assertFalse(user.profile.phone_verified)
