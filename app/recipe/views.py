from rest_framework.decorators import action  # For custom actions!
from rest_framework.response import Response  # For a custom response"
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (TagSerializer,
                                IngredientSerializer,
                                RecipeSerializer,
                                RecipeDetailSerializer,
                                RecipeImageSerializer)


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

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        # If the detail is requested, we use the RecipeDetailSerializer
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        # Else, we return the normal serializer class
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        # It will use the appropriate serializer
        # (determined according to the get_serializer_class function).
        serializer.save(user=self.request.user)

    # The detail URL (the one that contains the recipie id) is used.
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        # Get the object (based on the ID in URL).
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        # If it doesn't work:
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
