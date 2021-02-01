from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model


class UserManager(BaseUserManager):

    def construct_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email must be provided.')
        normalized_email = self.normalize_email(email)
        user = self.model(email=normalized_email, **extra_fields)
        user.set_password(password)
        return user

    def create_user(self, email, password=None, **extra_fields):
        user = self.construct_user(email, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.construct_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(PermissionsMixin, AbstractBaseUser):

    PASS_MIN_LENGTH = 5

    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()


class AttributeModel(models.Model):
    """A model that just contains a name and a user associated with it."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tag(AttributeModel):
    pass


class Ingredient(AttributeModel):
    pass


class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    minutes_required = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient', blank=True)
    tags = models.ManyToManyField('Tag', blank=True)

    def __str__(self):
        return self.title
