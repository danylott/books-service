from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    FINE_MULTIPLIER = 2

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class TypeChoices(models.TextChoices):
        FINE = "FINE"
        PAYMENT = "PAYMENT"

    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    type = models.CharField(max_length=20, choices=TypeChoices.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.PROTECT, related_name="payments"
    )
    session_url = models.URLField(max_length=1023, unique=True)
    session_id = models.CharField(max_length=150, unique=True)
    money_to_pay = models.DecimalField(
        "Borrowing total price", max_digits=7, decimal_places=2
    )

    def __str__(self) -> str:
        return f"{self.borrowing.id} - {self.type} - {self.status}"
