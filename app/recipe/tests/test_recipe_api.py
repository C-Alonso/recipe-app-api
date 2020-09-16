import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# The URL will end-up looking like: /api/recipe/recipes
RECIPES_URL = reverse('recipe:recipe-list')  # app:urlId


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_create_basic_recipe(self):
        """Test: creating recipe"""
        payload = {
            'title': 'Chocolate cheescake',
            'time_minutes': 60,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():  # getattr(recipe, key) is like recipe.key
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test: creating a recipe with tags"""
        tag = sample_tag(self.user, name='Dessert')
        tag2 = sample_tag(self.user, name='Vegan')
        payload = {
            'title': 'Mint cake',
            'tags': {tag.id, tag2.id},
            'time_minutes': 60,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        # We check that we received 2 tags back.
        self.assertEqual(len(tags), 2)
        # And that they were the right ones.
        self.assertIn(tag, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient = sample_ingredient(user=self.user, name='Cheese')
        ingredient2 = sample_ingredient(user=self.user, name='Cake')
        payload = {
            'title': 'Cheese cake',
            'ingredients': {ingredient.id, ingredient2.id},
            'time_minutes': 45,
            'price': 4.60
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        ingredients = recipe.ingredients.all()

        # We check that we received 2 ingredients back.
        self.assertEqual(len(ingredients), 2)
        # And that they were the right ones.
        self.assertIn(ingredient, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test: updating a recipe using PATCH"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Chipotle chicken',
            'tags': new_tag.id
            }

        url = detail_url(recipe.id)
        # We patch the Recipe.
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])

        # And now we check the tags.
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test: updating a recipe using PUT"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti Carbonara',
            'time_minutes': 25,
            'price': 5.00
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        # And we check that the recipe contains no tags
        # as we didn't add new ones in the payload.
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    """Test the image uploading feature"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@shevo.com',
            'testing321'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """Remove all the test image files on the system"""
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test: uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))  # <- 10x10 black square
            img.save(ntf, format='JPEG')
            ntf.seek(0)  # To start reading from the beginning of the file.
            # Multipart because we are not uploading json information.
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)  # The response contains an image.
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test: uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'noImage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
