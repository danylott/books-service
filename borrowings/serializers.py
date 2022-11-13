from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from notifications.telegram import send_telegram_notification
from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.views import create_stripe_payment


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "actual_return_date",
            "user",
            "payments",
        )

    def validate_book(self, value: Book) -> Book:
        if value.inventory == 0:
            raise ValidationError("Book is out of stock!")

        return value

    def create(self, validated_data) -> Borrowing:
        with transaction.atomic():
            instance = super().create(validated_data)
            instance.book.inventory -= 1
            instance.book.save()
            create_stripe_payment(
                self.context["request"], instance, Payment.TypeChoices.PAYMENT
            )
            send_telegram_notification(
                f"New book borrowing!\nData: {dict(validated_data)}"
            )
            return instance


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )
