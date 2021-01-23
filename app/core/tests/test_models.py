from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def create_user(self, email='abc@abc.com', password='abc123', **kwargs):
        return get_user_model().objects.create_user(
            email=email,
            password=password,
            **kwargs
        )

    def test_create_user_email_is_normalized(self):
        email = 'heLlo@EmAiL.com'
        normalized_email = 'heLlo@email.com'
        user = self.create_user(email=email)
        self.assertEqual(user.email, normalized_email)

    def test_create_user_password_is_same(self):
        password = 'Abc@123'
        user = self.create_user(password=password)
        self.assertTrue(user.check_password(password))

    def test_when_no_email_throws_ValueError(self):
        with self.assertRaises(ValueError):
            self.create_user(email=None)

    def test_create_superuser(self):
        email = 'hello@hello.com'
        password = 'hello123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
