import stripe
from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


def dict_to_readable_str(dict_to_convert: dict) -> str:
    return "; ".join(f"{key}: {value}" for key, value in dict_to_convert.items())


# TODO: add possibility to recreate stripe session
def create_stripe_payment(
    request: Request,
    borrowing: Borrowing,
    payment_type: Payment.TypeChoices,
    fine_multiplier: int = Payment.FINE_MULTIPLIER,
) -> Payment:
    product_data = {
        "name": borrowing.book.title,
        "description": dict_to_readable_str(
            {
                "author": borrowing.book.author,
                "cover": borrowing.book.cover,
                "daily_annual_fee": borrowing.book.daily_annual_fee,
                "borrow_date": borrowing.borrow_date,
                "expected_return_date": borrowing.expected_return_date,
            }
        ),
    }
    if payment_type == Payment.TypeChoices.FINE:
        product_data[
            "description"
        ] += f"; actual_return_date: {borrowing.actual_return_date}"
        total_price = fine_multiplier * borrowing.fine_price
    else:
        total_price = borrowing.total_price

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": product_data,
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(reverse("payments:payment-success"))
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("payments:payment-cancel")),
    )
    return Payment.objects.create(
        type=payment_type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )


class PaymentsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        queryset = super(PaymentsViewSet, self).get_queryset()

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(borrowing__user=self.request.user)

    @action(detail=False, methods=["GET"], url_name="success")
    def success(self, request: Request) -> Response:
        session_id = self.request.query_params.get("session_id")
        payments_queryset = Payment.objects.filter(session_id=session_id)
        if not session_id or not payments_queryset.exists():
            return Response(
                {"message": "Incorrect payment!"}, status=status.HTTP_400_BAD_REQUEST
            )

        payment_from_db = payments_queryset.get()
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        if stripe_session["payment_status"] != "paid":
            return Response(
                {
                    "message": "Payment was not successful! "
                    "Please contact support for more info."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_from_db.status = Payment.StatusChoices.PAID
        payment_from_db.save()

        return Response(
            PaymentSerializer(payment_from_db).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["GET"], url_name="cancel")
    def cancel(self, request: Request) -> Response:
        return Response(
            {
                "message": "Payment paused! "
                "Feel free to continue with your payment at any time!"
            },
            status=status.HTTP_204_NO_CONTENT,
        )
