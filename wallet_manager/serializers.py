"""Serializers for Wallet Manager"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import ActivityTracker, User, Wallet


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User instance
    """

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
        """
        Method to create new User instance.
        In this, the entered password will be validated as well like if it follows the expected format.

        If any of those conditions fail, then it will throw errors accordingly"""
        user = User.objects.create_user(**validated_data)
        try:
            validate_password(password=validated_data.get("password"), user=user)
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})
        return user


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for Wallet model
    """

    class Meta:
        model = Wallet
        fields = ["id", "balance", "wallet_id", "user_id"]


class ActivityTrackerSerializer(serializers.ModelSerializer):
    """
    Serializer for Activity Tracker model
    """

    class Meta:
        model = ActivityTracker
        fields = ["id", "transaction_type", "amount", "description", "created_at"]
