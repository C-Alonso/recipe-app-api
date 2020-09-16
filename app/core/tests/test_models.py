from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@shevo.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Tomato'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Pizza',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')  # This decorator's function generate a unique ID.
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that the image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
