from datetime import date, timedelta

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer
from users.serializers import UserSerializer
from notifications.telegram import send_telegram_notification


def check_borrowings_overdue() -> None:
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=date.today() - timedelta(days=1),
        actual_return_date__isnull=True,
    ).select_related("user")

    if not overdue_borrowings.exists():
        send_telegram_notification("No borrowings overdue today!")
        return

    for borrowing in overdue_borrowings:
        send_telegram_notification(
            "Borrowing overdue!\n"
            f"Borrowing: {BorrowingReadSerializer(borrowing).data}\n"
            f"User: {UserSerializer(borrowing.user).data}"
        )
