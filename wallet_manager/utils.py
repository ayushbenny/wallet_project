from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        print(user,"::user")
        token = super().get_token(user)
        token["email"] = user.user_email
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    print("enter here")
    serializer_class = CustomTokenObtainPairSerializer


class CustomRefreshTokenObtainPairView(TokenRefreshView):
    serializer_class = CustomTokenObtainPairSerializer
