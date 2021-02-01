from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
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

    def createTestTags(self, user=None):
        if user is None:
            user = self.user
        Tag.objects.create(user=user, name=TAG_1)
        Tag.objects.create(user=user, name=TAG_2)

    def test_tags_list(self):
        self.createTestTags()

        response = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_can_only_see_its_tags(self):
        other_user = get_user_model().objects.create_user(**USER_2)

        self.createTestTags(other_user)
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
