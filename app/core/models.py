
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin


# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an e-mail address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # Using the set_password() function provided by the AbstractBaseUser.
        user.set_password(password)
        user.save(using=self._db)  # To support multiple DB's.

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using e-mail instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # We costumize it so we can use the e-mail address
    USERNAME_FIELD = 'email'

    # DON'T FORGET TO ADD AUTH_USER_MODEL = 'core.User' (to settings.py file)
