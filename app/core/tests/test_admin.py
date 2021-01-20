from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminTests(TestCase):

    def setUp(self):

        self.client = Client()
        user = get_user_model()

        self.admin = user.objects.create_superuser(
            email='admin@email.com',
            password='admin123'
        )
        self.user = user.objects.create_user(
            email='user@email.com',
            password='user123'
        )

        self.client.force_login(self.admin)

    def test_user_is_listed(self):
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def assert_GET_returns_200(self, url, **kwargs):
        url = reverse(url, **kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_change_page(self):
        self.assert_GET_returns_200('admin:core_user_change', args=[self.user.id])

    def test_user_add_page(self):
        self.assert_GET_returns_200('admin:core_user_add')
