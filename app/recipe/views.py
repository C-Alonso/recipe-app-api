from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (TagSerializer,
                                IngredientSerializer,
                                RecipeSerializer)


class BaseRecipeAttrViewset(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user-owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # We overwrite the get_queryset() function.
    def get_queryset(self):
        """Returning objects for the current authenticated user only"""
        # The following line will work because authentication is required.
        return self.queryset.filter(user=self.request.user).order_by('-name')

    # We overwrite the create function.
    # The user will be the authenticated user.
    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewset):
    queryset = Tag.objects.all()

    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewset):
    queryset = Ingredient.objects.all()

    serializer_class = IngredientSerializer


# We provide all the CRUD functionalities with the ModelViewset.
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage Recipes in the DB"""

    serializer_class = RecipeSerializer

    queryset = Recipe.objects.all()

    authentication_classes = (TokenAuthentication,)

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve only the objects for the authenticated user."""
        return Recipe.objects.filter(user=self.request.user).order_by('-id')
