from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# The URL will end-up looking like: /api/recipe/recipes
RECIPES_URL = reverse('recipe:recipe-list')  # app:urlId


# The URL will end-up looking like: /api/recipe/recipes/id
def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


# Now we create a test recipe.
def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # Update overwrites or adds (if doesn't exist).
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Test: unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test: authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test: authenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@shevo.com',
            'testing321'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test: retrieving a list of recipes"""
        # We start by creating a couple of recipes
        sample_recipe(self.user)
        sample_recipe(self.user)

        # We visit the URL
        res = self.client.get(RECIPES_URL)

        # And let's retrieve the recipes to compare them to the response.
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test: retrieving recipes just for user"""
        # We are gonna need another user.
        user2 = get_user_model().objects.create_user(
            'test2@shevo.com',
            'testing322'
        )

        # And a recipe from him:
        sample_recipe(user2,
                      title='Sample recipe 2',
                      time_minutes=20,
                      price=10.00)

        # Now we create a couple of recipes from our user:
        sample_recipe(self.user)
        sample_recipe(self.user,
                      title='Sample recipe 3',
                      time_minutes=30,
                      price=15.00)

        # We visit the recipe endpoint:
        res = self.client.get(RECIPES_URL)

        # And we retrieve the recipes that belong to our user.
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        # many=True, so we get a list from the API (consistency)!
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # And we check tha we only received back 2 recipes:
        self.assertEqual(len(res.data), 2)

        # And that the recipe that we received is the one that we expect:
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test: viewing a Recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        # We generate now the URL.
        url = detail_url(recipe.id)
        res = self.client.get(url)

        # Many != True because we want to serialize a single object.
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)
