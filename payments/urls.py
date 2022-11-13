from django.urls import path, include
from rest_framework import routers

from .views import PaymentsViewSet

router = routers.DefaultRouter()
router.register("payments", PaymentsViewSet)

app_name = "payments"

urlpatterns = [
    path("", include(router.urls)),
]
