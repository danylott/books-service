from django.urls import path, include
from rest_framework import routers

from .views import BorrowingViewSet

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)

app_name = "borrowings"

urlpatterns = [
    path("", include(router.urls)),
]
