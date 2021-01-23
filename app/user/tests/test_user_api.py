from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import User

CREATE_USER_URL = reverse('user:create')
GET_TOKEN_URL = reverse('user:token')
USER_PROFILE_UPDATE_URL = reverse('user:update')

EMAIL_1 = 'hello@hello.com'
PASS_1 = 'pass123'

VALID_PAYLOAD_1 = {
    'email': EMAIL_1,
    'password': PASS_1,
    'name': 'Hello 1'
}

VALID_PAYLOAD_2 = {
    'email': 'email2@email.com',
    'password': 'passss123',
    'name': 'Hello 1'
}

VALID_PAYLOAD_1_WRONG_PASS = {
    'email': EMAIL_1,
    'password': PASS_1 + 'wrong',
}

VALID_PAYLOAD_NO_PASS_1 = {
    'name': 'no pass',
    'email': 'nopass@email.com'
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

    def assertGetTokenSuccess(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def assertGetTokenFaliure(self, response):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_token_valid(self):
        create_user(**VALID_PAYLOAD_1)
        response = self.client.post(GET_TOKEN_URL, VALID_PAYLOAD_1)
        self.assertGetTokenSuccess(response)

    def test_token_wrong_password(self):
        create_user(**VALID_PAYLOAD_1)
        response = self.client.post(GET_TOKEN_URL, VALID_PAYLOAD_1_WRONG_PASS)
        self.assertGetTokenFaliure(response)

    def test_token_no_email(self):
        payload = {'password': 'abcdefg'}
        response = self.client.post(GET_TOKEN_URL, payload)
        self.assertGetTokenFaliure(response)

    def test_token_non_existing_user(self):
        response = self.client.post(GET_TOKEN_URL, VALID_PAYLOAD_1)
        self.assertGetTokenFaliure(response)

    def test_get_user_profile_unauthorized(self):
        response = self.client.get(USER_PROFILE_UPDATE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(**VALID_PAYLOAD_1)
        self.client.force_authenticate(user=self.user)

    def assertUserIsValidFromResponse(self, response):
        self.assertNotIn('password', response.data)
        cur_user_info = {
            'name': self.user.name,
            'email': self.user.email
        }
        self.assertEqual(response.data, cur_user_info)

    def assertUserIsValidFromPayload(self, payload):
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])
        password = payload['password']
        if password:
            self.assertTrue(self.user.check_password(password))

    def test_get_user_profile_authorized(self):
        response = self.client.get(USER_PROFILE_UPDATE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertUserIsValidFromResponse(response)

    def test_post_user_profile_not_allowed(self):
        response = self.client.post(USER_PROFILE_UPDATE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        response = self.client.patch(USER_PROFILE_UPDATE_URL, VALID_PAYLOAD_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertUserIsValidFromPayload(VALID_PAYLOAD_2)
