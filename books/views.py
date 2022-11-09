from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Book
from .permisssions import IsAdminUserOrReadOnly
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAdminUserOrReadOnly,)
