"""Urls for Wallet Manager"""
from django.urls import path
from .utils import CustomRefreshTokenObtainPairView, CustomTokenObtainPairView
from .views import (
    ActivityTrackerAPIView,
    RegisterUserAPIView,
    TranserFundAPIView,
    WalletAPIView,
    WalletDepositAPIView,
    WalletWithdrawAPIView,
)


urlpatterns = [
    path("user/", RegisterUserAPIView.as_view(), name="register_user"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh/",
        CustomRefreshTokenObtainPairView.as_view(),
        name="token_refresh",
    ),
    path("api/wallet/", WalletAPIView.as_view()),
    path("api/wallet/deposit/", WalletDepositAPIView.as_view()),
    path("api/wallet/withdraw/", WalletWithdrawAPIView.as_view()),
    path("api/activity_tracker/", ActivityTrackerAPIView.as_view()),
    path("api/transfer_funds/", TranserFundAPIView.as_view()),
]
