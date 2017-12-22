from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from ..base import BaseTests


class SignupApiTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.total_users = User.objects.count()

    def test_with_valid_data(self):
        response = self.client.post('/api/users/', {
            'email': 'johndoe@example.com',
            'username': 'johndoe',
            'password': 'secretpass',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), self.total_users+1)
        user = User.objects.last()
        self.assertEqual(user.email, 'johndoe@example.com')
        self.assertEqual(user.username, 'johndoe')
        data = response.json()
        self.assertEqual(data['token'], user.auth_token.key)
        self.assertTrue('email' not in data)
        self.assertTrue('password' not in data)

    def test_unique_email_and_unique_username(self):
        response = self.client.post('/api/users/', {
            'email': self.bob.email,
            'username': self.bob.username,
            'password': 'secretpass',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), self.total_users)
        errors = response.json()
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors['email'][0], 'This field must be unique.')
        self.assertEqual(errors['username'][0], 'This field must be unique.')


class TokenAuthenticationTests(BaseTests):
    def test_all_users_have_auth_token(self):
        self.assertIsNotNone(self.bob.auth_token.key)
        self.assertIsNotNone(self.alice.auth_token.key)

    def test_valid_login(self):
        response = self.client.post('/api-token-auth/', {
            'username': 'bob',
            'password': 's3cr3t',
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'), 
            {'token': self.bob.auth_token.key},
        )

        response = self.client.post('/api-token-auth/', {
            'username': 'alice',
            'password': 's3cr3t',
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'), 
            {'token': self.alice.auth_token.key},
        )

    def test_invalid_login(self):
        response = self.client.post('/api-token-auth/', {
            'username': 'bob',
            'password': 'xxx',
        })

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content.decode('utf-8'), {
            'non_field_errors': ['Unable to log in with provided credentials.']
        })


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
