from datetime import date

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


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

    @action(detail=True, methods=["POST"], name="return")
    def return_borrowing(self, request: Request, pk: int = None) -> Response:
        borrowing = self.get_object()
        borrowing.actual_return_date = date.today()
        borrowing.save()
        borrowing.refresh_from_db()

        return Response(BorrowingSerializer(borrowing).data, status=status.HTTP_200_OK)
