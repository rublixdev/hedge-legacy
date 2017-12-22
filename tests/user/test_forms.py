import os
from os.path import join, dirname, abspath

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.user.forms import UserProfileForm, ChangePasswordForm
from ..base import BaseTests

FIXTURES_DIR = join(dirname(dirname(abspath(__file__))), 'fixtures')
ASSETS_DIR = join(dirname(dirname(abspath(__file__))), 'assets')


class UserProfileFormTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.sample_image = open(os.path.join(ASSETS_DIR, 'sample_image.png'), 'rb')
        self.sample_textfile = open(os.path.join(ASSETS_DIR, 'lorem.txt'), 'rb')

    def tearDown(self):
        self.sample_image.close()
        self.sample_textfile.close()

    def test_form_should_require_user_parameter(self):
        try:
            form = UserProfileForm()
            self.fail('should raise exception here')
        except Exception: 
            pass
        try:
            form = UserProfileForm(user=self.bob)
        except Exception:
            self.fail('Should not raise exception here')

    def test_form_should_define_correct_fields(self):
        fields = ['name', 'email', 'picture', 'bio', 'website']
        form = UserProfileForm(user=self.bob)

        self.assertEqual(len(form.fields), len(fields))
        for field in fields:
            self.assertTrue(field in form.fields)
            self.assertIsNotNone(form.fields[field])

    def test_form_should_set_instance_and_initial_email(self):
        form = UserProfileForm(user=self.bob)

        self.assertEqual(form.instance, self.bob.profile)
        self.assertEqual(form.initial['email'], self.bob.email)

    def test_with_invalid_data(self):
        f = self.sample_textfile
        form = UserProfileForm(
            dict(email='xxx'),
            dict(picture=SimpleUploadedFile(f.name, f.read())),
            user=self.bob,
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['email'][0], 
            'Enter a valid email address.',
        )
        self.assertEqual(
            form.errors['picture'][0],
            'Upload a valid image. '
            'The file you uploaded was either not an image or a corrupted image.',
        )

    def test_with_valid_data(self):
        f = self.sample_image
        form = UserProfileForm(
            dict(email='user@example.com'),
            dict(picture=SimpleUploadedFile(f.name, f.read())),
            user=self.bob,
        )

        self.assertTrue(form.is_valid())


class ChangePasswordFormTests(BaseTests):
    def test_form_should_define_correct_fields(self):
        fields = ['current_password', 'new_password', 'confirm_new_password']        
        form = ChangePasswordForm(user=self.bob)

        self.assertEqual(len(form.fields), len(fields))
        for f in fields:
            self.assertTrue(f in form.fields)
            self.assertIsNotNone(form.fields[f])

    def test_form_should_require_user_parameter(self):
        try:
            form = ChangePasswordForm()
            self.fail('Should raise Exception here.')
        except Exception: 
            pass
        try:
            form = ChangePasswordForm(user=self.bob)
        except KeyError:
            self.fail('Should not raise Exception here.')

    def test_with_invalid_data(self):
        data = dict(
            current_password='xxxxx',
            new_password='yyy',
            confirm_new_password='zzzzz',
        )
        form = ChangePasswordForm(data, user=self.bob)

        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertEqual(
            form.errors['current_password'][0], 
            'Please enter the correct password',
        )
        self.assertEqual(
            form.errors['new_password'][0],
            'Ensure this value has at least 5 characters (it has 3).',
        )
        self.assertEqual(
            form.errors['confirm_new_password'][0],
            'This value should match with the new password',
        )

    def test_with_valid_data(self):
        data = dict(
            current_password='s3cr3t',
            new_password='secret',
            confirm_new_password='secret',
        )
        form = ChangePasswordForm(data, user=self.bob)

        self.assertTrue(form.is_valid())
