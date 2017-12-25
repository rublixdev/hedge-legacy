from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from ..base import BaseTests


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
