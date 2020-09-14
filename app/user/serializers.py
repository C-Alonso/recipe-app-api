from django.contrib.auth import get_user_model, authenticate
# To get automatic translations for output messages:
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()  # Returns user model class
        # Fields we want to make accesible
        # on our API (create or read).
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # We overwrite the create function.
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # None as default (case no password was provided).
        password = validated_data.pop('password', None)
        # We will user the default ModelSerializer update function,
        # and we will update everything (but the password, which was
        # popped above).
        # Note: the password is now contained in the password variable.
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    # We modify it to accept the email instead of the username.
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            # Note: _ is there in case translations are required.
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        # We send back the validated user.
        attrs['user'] = user
        return attrs
