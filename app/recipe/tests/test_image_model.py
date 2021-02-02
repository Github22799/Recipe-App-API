import os
import tempfile
import PIL
from django.test import TestCase
from rest_framework import status
from core.models import Image
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from recipe.serializers import ImageSerializer

IMAGES_URL = reverse('recipe:image-list')


class UnauthorizedImageTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_is_required(self):
        response = self.client.get(IMAGES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedImageTests(TestCase):

    def create_user(self, email='hello@hoho.com', password='hoho123'):
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        return user

    def create_image(self, user=None, image='images/1.jpg'):
        if user is None:
            user = self.user
        return Image.objects.create(user=user, image=image)

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(email='hola@oo.com')
        self.client.force_authenticate(self.user)

    def test_list_images(self):
        self.create_image()
        self.create_image()
        response = self.client.get(IMAGES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_images_are_limited_to_its_user(self):
        other_user = self.create_user()
        self.create_image(other_user)
        self.create_image()
        self.create_image()

        images = Image.objects.filter(user=self.user)
        serializer = ImageSerializer(images, many=True)
        response = self.client.get(IMAGES_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(serializer.data, response.data)

    def test_upload_valid_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            image = PIL.Image.new('RGB', (10, 10))
            image.save(ntf, format='JPEG')
            ntf.seek(0)
            response = self.client.post(IMAGES_URL, {'image': ntf}, format='multipart')
        images = Image.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(images.count(), 1)
        self.assertTrue(os.path.exists(images[0].image.path))

    def test_upload_invalid_image(self):
        response = self.client.post(IMAGES_URL, {'image': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)