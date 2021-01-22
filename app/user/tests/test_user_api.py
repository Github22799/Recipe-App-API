from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import User

CREATE_USER_URL = reverse('user:create')

VALID_PAYLOAD_1 = {
    'email': 'hello@hello.com',
    'password': 'pass123',
    'name': 'Hello 1'
}

SHORT_PASSWORD_PAYLOAD = {
    'email': 'hello@hello.com',
    'password': 'a' * (User.PASS_MIN_LENGTH - 1),
    'name': 'Hello 1'
}


def get_user_manager():
    return get_user_model().objects


def filter_users(**kwargs):
    return get_user_manager().filter(**kwargs)

def get_user(**kwargs):
    return get_user_manager().get(**kwargs)


def create_user(**kwargs):
    return get_user_manager().create_user(**kwargs)


class UnauthorizedUserAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_valid_user_create(self):
        response = self.client.post(CREATE_USER_URL, VALID_PAYLOAD_1)

        user = get_user(**response.data)
        password = VALID_PAYLOAD_1['password']

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(password))
        self.assertNotIn(password, response.data)

    def test_duplicate_user_create(self):
        create_user(**VALID_PAYLOAD_1)
        response = self.client.post(CREATE_USER_URL, VALID_PAYLOAD_1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password_user_create(self):
        response = self.client.post(CREATE_USER_URL, SHORT_PASSWORD_PAYLOAD)

        user_exists = filter_users(**response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)
