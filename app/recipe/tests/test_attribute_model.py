from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

# TODO testing the Tag model instead of the Attribute model
#  because I don't know a way to generate urls and send
#  requests to a model where its urls won't be registered.

TAG_1 = 'Vegan'
TAG_2 = 'Dessert'
TAG_3 = 'Breakfast'

USER_1 = {
    'email': 'hello@email.com',
    'password': 'hello123',
    'name': 'name name'
}

USER_2 = {
    'email': 'hello2@email.com',
    'password': 'hello123',
    'name': 'name name 2'
}

TAGS_URL = reverse('recipe:tag-list')


class UnauthorizedTagTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedTagTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(**USER_1)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def createTag(self, user=None, name=TAG_1):
        if user is None:
            user = self.user
        tag = Tag.objects.create(user=user, name=name)
        return tag

    def createTwoTestTags(self, user=None):
        tag1 = self.createTag(user=user, name=TAG_1)
        tag2 = self.createTag(user=user, name=TAG_2)
        return [tag1, tag2]

    def createTestRecipe(self, images=None, tags=None, ingredients=None, **kwargs):

        if images is None:
            images = []
        if ingredients is None:
            ingredients = []
        if tags is None:
            tags = []

        payload = {
            'user': self.user,
            'title': 'Recipe abcd',
            'minutes_required': 5,
            'price': 55
        }
        payload.update(kwargs)
        recipe = Recipe.objects.create(**payload)
        recipe.images.set(images)
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)
        return

    def test_tags_list(self):
        self.createTwoTestTags()

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_can_only_see_its_tags(self):
        other_user = get_user_model().objects.create_user(**USER_2)

        self.createTwoTestTags(other_user)
        tag = Tag.objects.create(user=self.user, name=TAG_1)

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_valid_tag(self):
        payload = {
            'name': TAG_1,
            'user': self.user
        }
        self.client.post(TAGS_URL, payload)
        exists = Tag.objects.filter(**payload).exists()
        self.assertTrue(exists)

    def test_create_empty_tag(self):
        payload = {
            'name': '',
        }
        response = self.client.post(TAGS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_assigned_only_tags(self):
        tag1 = self.createTag(name='a')
        tag2 = self.createTag(name='b')
        unassigned_tag = self.createTag(name='c')
        self.createTestRecipe(tags=[tag1])
        self.createTestRecipe(tags=[tag2])

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        # TODO see why it doesn't work when you don't pass the tags in a list...
        serializer1 = TagSerializer([tag1], many=True)
        serializer2 = TagSerializer([tag2], many=True)
        unassigned_serializer = TagSerializer([unassigned_tag], many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(serializer1.data[0], response.data)
        self.assertIn(serializer2.data[0], response.data)
        self.assertNotIn(unassigned_serializer.data[0], response.data)

    def test_list_assigned_only_tags_distinct(self):
        tag = self.createTag(name='a')
        self.createTestRecipe(tags=[tag])
        self.createTestRecipe(tags=[tag])

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
