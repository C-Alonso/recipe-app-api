from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag
from recipe.serializers import TagSerializer


# Create your views here.
class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()

    serializer_class = TagSerializer

    # We overwrite the get_queryset() function.
    def get_queryset(self):
        """Returng objects for the current authenticated user only"""
        # The following line will work because authentication is required.
        return self.queryset.filter(user=self.request.user).order_by('-name')
