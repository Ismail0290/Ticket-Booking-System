from django.test import TestCase, Client
from django.urls import reverse

from .models import Users  # Adjust the import based on your actual model names and structure

class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
        self.user = Users.objects.create_user(**self.user_data)

    def test_login(self):
        response = self.client.get(reverse('login'))  # Replace 'login' with your actual URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')