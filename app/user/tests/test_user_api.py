from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test: creating user with valid payload is successful"""
        payload = {
            'email': 'test@shevo.com',
            'password': 'testpass',
            'name': 'Test Shevo'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # The data should have returned the user by now.
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # We check that the actual password wasn't returned,
        # as that would suppose a security vulnerability.
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test: creating a user that already exists fails"""
        payload = {
            'email': 'test@shevo.com',
            'password': 'testpass',
            'name': 'Test'
        }
        # We create the user.
        create_user(**payload)
        # And we try to create it again.
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):  # Implemented on the serializer.
        """Test: the password must be longer that 5 characters"""
        payload = payload = {
            'email': 'test@shevo.com',
            'password': 'pwd',
            'name': 'Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        # We check if the user was created.
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        # (It shouldn't).
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test: a token is created for the user"""
        payload = {
            'email': 'test@shevo.com',
            'password': 'testPwd',
            'name': 'Test'
        }
        # We create the user.
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        # We assert that the response contains a token.
        # We don't re-test that the token work.
        # (that's already done by django).
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test: a token is not created if invalid credentials are provided"""
        payload = {
            'email': 'test@shevo.com',
            'password': 'testPwd',
            'name': 'Test'
        }
        # We create the user.
        create_user(**payload)

        wrongPayload = {
            'email': 'test@shevo.com',
            'password': 'wrongPwd',
            'name': 'Test'
        }

        res = self.client.post(TOKEN_URL, wrongPayload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test: token is not created if user doesn't exist"""
        payload = {
            'email': 'test@shevo.com',
            'password': 'testPwd'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test: email and password are required"""
        payload = {
            'email': 'test',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
