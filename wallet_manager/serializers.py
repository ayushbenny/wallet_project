from rest_framework import serializers
from wallet_manager.regexp_validators import PasswordValidator
from .models import ActivityTracker, User, Wallet


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        password_obj = PasswordValidator.validate_password(value)
        return password_obj

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "user_email",
            "password",
            "phone_number",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "balance", "wallet_id", "user_id"]


class ActivityTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTracker
        fields = ["id", "transaction_type", "amount", "description", "created_at"]
