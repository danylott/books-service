from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("users:register")
TOKEN_PAIR_URL = reverse("users:token_obtain_pair")
USER_MANAGE_URL = reverse("users:me")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_forbid_unauthorized(self):
        res = self.client.get(USER_MANAGE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user(self):
        payload = {
            "email": "test@test.com",
            "password": "shall_i_pass?",
            "first_name": "Gandalf",
            "last_name": "Grey",
        }

        res = self.client.post(CREATE_USER_URL, payload)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload["password"]))

    def test_password_less_6_chars(self):
        payload = {
            "email": "test@test.com",
            "password": "nope",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        user_created = get_user_model().objects.filter(email=payload["email"]).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_created)

    def test_create_user_token(self):
        payload = {
            "email": "test@test.com",
            "password": "that_should_work_123",
        }
        create_user(**payload)
        res = self.client.post(TOKEN_PAIR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", res.data)
        self.assertIn("access", res.data)

    def test_create_token_wo_email_or_pass_fail(self):
        res = self.client.post(
            TOKEN_PAIR_URL, {"email": "test@test.com", "password": ""}
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)


class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="IHaveThePowah!!",
            first_name="Orson",
            last_name="Wells",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(USER_MANAGE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "id": self.user.id,
                "email": self.user.email,
                "is_staff": self.user.is_staff,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
            },
        )

    def test_post_me_not_allowed(self):
        res = self.client.post(USER_MANAGE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_users_own_profile(self):
        payload = {
            "email": "test@test.com",
            "password": "science_fiction_rules:)",
            "first_name": "Robert",
            "last_name": "Sheckley",
        }
        res = self.client.patch(USER_MANAGE_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload["email"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
