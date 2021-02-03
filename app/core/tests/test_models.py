from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Tag, Recipe, get_image_upload_path, Image


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

    def test_tag_str_representation(self):
        tag = Tag.objects.create(
            name='TagName',
            user=self.create_user()
        )
        self.assertEqual(str(tag), tag.name)

    def test_recipe_str_representation(self):
        recipe = Recipe.objects.create(
            user=self.create_user(),
            title='hello',
            minutes_required=5,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_image_str_representation(self):
        image = Image(user=self.create_user(), image='', description='abc')
        self.assertEqual(str(image), image.description)

    @patch('uuid.uuid4')
    def test_image_upload_filename(self, mock_object):
        uuid = 'uuid'
        extension = 'jpg'
        mock_object.return_value = uuid
        result_path = get_image_upload_path(instance=None, filename=f'image.{extension}')
        expected_path = f'upload/recipe/{uuid}.{extension}'
        self.assertEqual(result_path, expected_path)
