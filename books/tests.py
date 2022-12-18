from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer
from users.tests import create_user

BOOK_URL = reverse("books:book-list")


def sample_books(**params):
    defaults = {
        "title": "Sample book",
        "author": "Sample author",
        "inventory": 10,
        "daily_annual_fee": 1.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)

  def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class PublicBooksApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_post_books(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "inventory": 10,
            "daily_annual_fee": 1.00,
        }

        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        
        class PrivateBookApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_books(self):
        sample_books()

        response = self.client.get(BOOK_URL)

        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

def test_post_books(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "inventory": 10,
            "daily_annual_fee": 1.00,
        }

        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AdminBookApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_books(self):
        payload = {
            "title": "Sample book",
            "author": "Sample author",
            "inventory": 10,
            "daily_annual_fee": 1.00,
            "cover": "HARD",
        }

        response = self.client.post(BOOK_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_book(self):
        sample_books()

        response = self.client.get(f"{BOOK_URL}1/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

def test_put_book(self):
        sample_books()

        response = self.client.put(f"{BOOK_URL}1/", {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_book(self):
        sample_books()

        response = self.client.delete(f"{BOOK_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
