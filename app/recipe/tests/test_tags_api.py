from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test: login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    """Test the authorized user tags API"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@shevo.com',
            'testing321'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test: retreiving tags"""
        # We create a couple of tags
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # And now we try to retrieve them
        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@shevo.com',
            'testing123'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Snacks')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # Two tags exist at this point.
        # Check that the name of the tags is Snacks (in this case).
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test: creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()  # Returns a boolean.

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test: creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test: filter tags assigned to recipes"""
        unassigned_tag = Tag.objects.create(user=self.user, name='Unassigned tag')
        recipe = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        assigned_tag = Tag.objects.create(user=self.user, name='Assigned tag')
        recipe.tags.add(assigned_tag)

        res = self.client.get(
            TAGS_URL,
            {'assigned_only': 1}  # True}
        )

        serializer1 = TagSerializer(assigned_tag)
        serializer2 = TagSerializer(unassigned_tag)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    # By default, django filters will return an item for each coincidence,
    # which may result in duplicated values. We are going to test that that
    # doesn't happen:
    def test_retrieve_tags_assigned_unique(self):
        """Test: filtering assigned tags returns unique items"""
        unassigned_tag = Tag.objects.create(user=self.user, name='Unassigned tag')
        assigned_tag = Tag.objects.create(user=self.user, name='Assigned tag')
        recipe = Recipe.objects.create(
            title='Recipe 1',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        recipe.tags.add(assigned_tag)
        recipe2 = Recipe.objects.create(
            title='Recipe 2',
            time_minutes=6,
            price=3.50,
            user=self.user
        )
        recipe2.tags.add(assigned_tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        # We check that, even though a tag has been assigned to 2 recipes,
        # the result will bring back the tag only once.
        self.assertEqual(len(res.data), 1)
