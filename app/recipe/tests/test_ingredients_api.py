from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITest(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test: login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test: private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@shevo.com',
            'testing321'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test: retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test: only ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@shevo.com',
            'testing123'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Kurkuma')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test: create new ingredient"""
        payload = {'name': 'Carrot'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test: creating invalid ingredient fails"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Shevo'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='More Shevo'
        )
        recipe = Recipe.objects.create(
            title='Shevo al horno',
            time_minutes=5,
            price=5,
            user=self.user
        )
        recipe.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer = IngredientsSerializer(ingredient)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    # We check that, even though an ingredient has been assigned to 2 recipes,
    # the result will bring back the ingredient only once.
    def test_retrieve_ingredients_assigned_unique(self):
        """Test: filtering assigned ingredients returns unique items"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Shevo'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='More Shevo'
        )
        recipe = Recipe.objects.create(
            title='Shevo al horno',
            time_minutes=5,
            price=5,
            user=self.user
        )
        recipe.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Shevo a la leña',
            time_minutes=45,
            price=20,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

