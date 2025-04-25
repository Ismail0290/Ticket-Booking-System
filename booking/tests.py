from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User  

class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_page_access(self):
        # Test that the login page is accessible
        response = self.client.get(reverse('login'))  # Replace 'login' with your actual URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login(self):
        # Test a successful login
        response = self.client.post(reverse('login'), {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect on successful login
        self.assertRedirects(response, '/')  # Replace '/' with your actual redirect URL
