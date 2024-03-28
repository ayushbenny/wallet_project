from rest_framework import serializers
from .models import ActivityTracker, User, Wallet


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "user_email",
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
