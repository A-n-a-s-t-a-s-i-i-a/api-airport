from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword",
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_create_user(self):
        """Test creating a new user"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
        }
        response = self.client.post("/api/user/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(get_user_model().objects.get(id=2).username, "newuser")

    def test_login_user(self):
        """Test user can log in and get an auth token"""
        response = self.client.post(
            "/api/user/token/",
            {
                "username": self.user_data["username"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)  # Check for JWT access token

    def test_manage_user(self):
        """Test retrieving and updating the authenticated user"""
        response = self.client.post(
            "/api/user/token/",
            {
                "username": self.user_data["username"],
                "password": self.user_data["password"],
            },
            format="json",
        )
        token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        response = self.client.get("/api/user/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_data["username"])

        new_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "password": "newpassword",
        }
        response = self.client.put("/api/user/me/", new_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "updateduser")
        self.assertEqual(response.data["email"], "updated@example.com")
