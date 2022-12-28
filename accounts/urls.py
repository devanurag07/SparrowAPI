from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import SimpleRouter
from .views import AuthAPI

router = SimpleRouter()
router.register("auth", AuthAPI, basename="auth")

urlpatterns = router.urls
