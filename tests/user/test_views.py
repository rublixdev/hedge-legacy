from unittest.mock import patch
from collections import namedtuple

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user
from django.conf import settings

from ..base import BaseTests


class SignupTests(BaseTests):
    def test_submit_valid_data(self):
        numrows = User.objects.count()

        response = self.client.post('/user/signup/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'password1': 's3cr3tp4ss',
            'password2': 's3cr3tp4ss',
            'email': 'john.doe@example.com',
            'phone_country_code': '62',
            'phone_number': '+621234567890',
            'wallet_address': '0x123f681646d4a755815f9cb19e1acc8565a0c2ac',
            'date_of_birth': '01/01/1970',
            'terms': '1',
        })

        self.assertEqual(User.objects.count(), numrows+1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/confirm-email/')

    def test_duplicate_email(self):
        response = self.client.post('/user/signup/', {'email': self.bob.email})

        self.assertEqual(
            response.context['form'].errors['email'][0], 
            'A user is already registered with this e-mail address.',
        )

    def test_duplicate_phone_number(self):
        response = self.client.post('/user/signup/', {
            'phone_country_code': self.bob.profile.phone_country_code,
            'phone_number': self.bob.profile.phone_number,
        })

        self.assertEqual(
            response.context['form'].errors['phone_number'][0],
            'A user is already registered with this phone number.',
        )


class LoginTests(BaseTests):
    def test_with_verified_email_and_phone_number(self):
        alice_email = self.alice.emailaddress_set.first()
        alice_email.verified = True
        alice_email.save()
        self.alice.profile.phone_verified = True
        self.alice.profile.save()

        response = self.client.post('/user/login/', {
            'login': self.alice.username,
            'password': 's3cr3t',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/')
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_with_invalid_credentials(self):
        response = self.client.post('/user/login/', {
            'login': 'xxx',
            'password': 'yyy',
        })

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated())

    def test_with_unverified_email(self):
        alice_email = self.alice.emailaddress_set.first()
        alice_email.verified = False
        alice_email.save()
        self.alice.profile.phone_verified = True
        self.alice.profile.save()

        response = self.client.post('/user/login/', {
            'login': self.alice.username,
            'password': 's3cr3t',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/confirm-email/')

    @patch('requests.post')
    def test_with_unverified_phone_number(self, requests_mock):
        alice_email = self.alice.emailaddress_set.first()
        alice_email.verified = True
        alice_email.save()
        self.alice.profile.phone_verified = False
        self.alice.profile.save()

        response = self.client.post('/user/login/', {
            'login': self.alice.username,
            'password': 's3cr3t',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/confirm_phone.html')
        requests_mock.assert_called_once_with(
            'https://api.authy.com/protected/json/phones/verification/start' \
            '?api_key=%s' % settings.TWILIO_API_KEY,
            data={
                'via': 'sms',
                'country_code': self.alice.profile.phone_country_code,
                'phone_number': self.alice.profile.phone_number,
            }
        )


class PhoneVerificationTests(BaseTests):
    def setUp(self):
        super().setUp()
        alice_email = self.alice.emailaddress_set.first()
        alice_email.verified = True
        alice_email.save()
        self.alice.profile.phone_verified = False
        self.alice.profile.save()

        phone_hash = self.alice.profile.phone_number_hash
        self.verification_url = '/user/confirm-phone/?h=%s' % phone_hash

    @patch('requests.post')
    def test_create_verification_code_on_load(self, requests_mock):
        response = self.client.get(self.verification_url)

        requests_mock.assert_called_once_with(
            'https://api.authy.com/protected/json/phones/verification/start' \
            '?api_key=%s' % settings.TWILIO_API_KEY,
            data={
                'via': 'sms',
                'country_code': self.alice.profile.phone_country_code,
                'phone_number': self.alice.profile.phone_number,
            }
        )
        self.alice.profile.refresh_from_db()
        self.assertFalse(self.alice.profile.phone_verified)

    @patch('requests.get')
    def test_submit_correct_verification_code(self, requests_mock):
        Response = namedtuple('Response', 'status_code')
        requests_mock.return_value = Response(status_code=200)

        response = self.client.post(self.verification_url, {
            'verification_code': '12345',
        })

        requests_mock.assert_called_once_with(
            'https://api.authy.com/protected/json/phones/verification/check',
            params={
                'api_key': settings.TWILIO_API_KEY,
                'country_code': self.alice.profile.phone_country_code,
                'phone_number': self.alice.profile.phone_number,
                'verification_code': '12345',
            },
        )
        self.alice.profile.refresh_from_db()
        self.assertTrue(self.alice.profile.phone_verified)

    @patch('requests.get')
    def test_submit_incorrect_verification_code(self, requests_mock):
        Response = namedtuple('Response', 'status_code')
        requests_mock.return_value = Response(status_code=400)

        response = self.client.post(self.verification_url, {
            'verification_code': '00000',
        })

        requests_mock.assert_called_once_with(
            'https://api.authy.com/protected/json/phones/verification/check',
            params={
                'api_key': settings.TWILIO_API_KEY,
                'country_code': self.alice.profile.phone_country_code,
                'phone_number': self.alice.profile.phone_number,
                'verification_code': '00000',
            },
        )
        self.alice.profile.refresh_from_db()
        self.assertFalse(self.alice.profile.phone_verified)


class ChangePasswordTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.client.login(username='bob', password='s3cr3t')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get('/user/change_password/')

        self.assertRedirects(
            response, 
            '/user/login/?next=/user/change_password/',
        )

    def test_render_the_correct_template(self):
        response = self.client.get('/user/change_password/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/change_password.html')

    def test_with_valid_data(self):
        response = self.client.post('/user/change_password/', {
            'current_password': 's3cr3t',
            'new_password': 'secret',
            'confirm_new_password': 'secret',
        }, follow=True)

        msg = list(response.context['messages'])

        self.assertTrue(len(msg), 1)
        self.assertEqual(str(msg[0]), 'Password successfully changed.')
        self.assertIsNotNone(authenticate(username='bob', password='secret'))

    def test_with_invalid_data(self):
        response = self.client.post('/user/change_password/', {
            'current_password': 'wrongpass',
            'new_password': 'xxx',
            'confirm_new_password': 'yyyyy',
        })

        self.assertEqual(len(response.context['form'].errors), 3)
        self.assertFormError(
            response, 
            'form', 
            'current_password',
            'Please enter the correct password',
        )
        self.assertFormError(
            response,
            'form',
            'new_password',
            'Ensure this value has at least 5 characters (it has 3).',
        )
        self.assertFormError(
            response,
            'form',
            'confirm_new_password',
            'This value should match with the new password',
        )
