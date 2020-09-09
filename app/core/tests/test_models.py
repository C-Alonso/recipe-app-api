
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test: successfull creation of a new user whith an email"""
        testEmail = 'carlos@hotmail.com'
        testPassword = 'Testing321'
        user = get_user_model().objects.create_user(
            email=testEmail,
            password=testPassword
        )

        self.assertEqual(user.email, testEmail)

        self.assertTrue(user.check_password(testPassword))

    def test_new_user_email_normalized(self):
        """"Test: the email for a new user is normalized"""
        email = 'carlos@HoTmAiL.cOm'
        user = get_user_model().objects.create_user(email, 'Testing321')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test: creating user with no e-mail raises an error"""
        # Anything in here should raise the ValueError
        # (otherwise, the test fails)
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Testing321')

    def test_create_new_superuser(self):
        """Test: creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'carlos@hotmail.com',
            'Testing321'
        )
        # Both included as part of the PermissionsMixin
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
