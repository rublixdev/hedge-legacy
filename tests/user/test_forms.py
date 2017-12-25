import os
from os.path import join, dirname, abspath

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.user.forms import SignupForm, ChangePasswordForm
from ..base import BaseTests

FIXTURES_DIR = join(dirname(dirname(abspath(__file__))), 'fixtures')
ASSETS_DIR = join(dirname(dirname(abspath(__file__))), 'assets')


class SignupFormTests(BaseTests):
    def test_with_valid_data(self):
        form = SignupForm({
            'name': 'sample user',
            'phone_number': '082141674751',
            'wallet_address': '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2',
            'date_of_birth': '1/1/1970',
            'terms': '1',
        })

        self.assertTrue(form.is_valid())

    def test_name_validation(self):
        form = SignupForm({'name': 'a'})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['name'][0], 
            'Ensure this value has at least 6 characters (it has 1).',
        )

    def test_phone_number_validation(self):
        number_tests = [
            ('123', 'Ensure this value has at least 12 characters (it has 3).'),
            ('+62 aaa 111 222 333 444', 'Only numbers, spaces, hyphens, and parentheses allowed.'),
        ]

        for number, errmsg in number_tests:
            form = SignupForm({'phone_number': number})

            self.assertFalse(form.is_valid())
            self.assertEqual(form.errors['phone_number'][0], errmsg)

    def test_wallet_address_validation(self):
        form = SignupForm({'wallet_address': '1AGNa15ZQXAZUgFiqJ3i7Z2DPU2J6hW62i'})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['wallet_address'][0], 'Invalid wallet address.')

    def test_date_of_birth_validation(self):
        form = SignupForm({'date_of_birth': '1/1/2017'})

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['date_of_birth'][0],
            'You have to be 33 years old or older.',
        )


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
