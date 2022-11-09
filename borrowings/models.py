from django.conf import settings
from django.db import models
from django.db.models import Q, F

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(expected_return_date__gt=F("borrow_date")),
                name="check_expected_return_date",
            ),
            models.CheckConstraint(
                check=Q(actual_return_date__gte=F("borrow_date")),
                name="check_actual_return_date",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.book}: {self.borrow_date} - {self.expected_return_date}."
