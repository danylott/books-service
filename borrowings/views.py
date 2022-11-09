from datetime import date
from typing import Type

from django.db.models import QuerySet
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingReadSerializer


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ("list", "retrieve"):
            return BorrowingReadSerializer

        return super().get_serializer_class()

    @action(
        detail=True, methods=["POST"], url_path="return", serializer_class=Serializer
    )
    def return_borrowing(self, request: Request, pk: int = None) -> Response:
        # TODO: add logic, if actual_return_date > expected_return_date
        borrowing = self.get_object()
        borrowing.actual_return_date = date.today()
        borrowing.book.inventory += 1
        borrowing.save()
        borrowing.refresh_from_db()

        return Response(BorrowingSerializer(borrowing).data, status=status.HTTP_200_OK)

    def perform_create(self, serializer: BorrowingSerializer):
        return serializer.save(user=self.request.user)
