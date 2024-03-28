"""Models for Wallet Manager"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

from .regexp_validators import NameValidator, PhoneNumberValidator


class User(AbstractUser):
    """
    Custom User model representing users of the Wallet Manager.

    Attributes:
        first_name (str): First name of the user.
        last_name (str): Last name of the user.
        user_email (str): Email address of the user (unique).
        user_id (UUID): Unique identifier for the user.
        phone_number (str): Phone number of the user.
        is_active (bool): Flag indicating whether the user account is active.
        created_at (DateTime): Timestamp indicating when the user account was created.
        updated_at (DateTime): Timestamp indicating when the user account was last updated.
    """

    first_name = models.CharField(
        max_length=50, null=False, blank=False, validators=[NameValidator.validate_name]
    )
    last_name = models.CharField(
        max_length=50, null=False, blank=False, validators=[NameValidator.validate_name]
    )
    user_email = models.EmailField(unique=True)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(
        max_length=15, validators=[PhoneNumberValidator.validate_phone_number]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User -> {self.user_email}"


class Wallet(models.Model):
    """
    Model representing a wallet associated with a user in the Wallet Manager.

    Attributes:
        balance (Decimal): Current balance of the wallet.
        wallet_id (UUID): Unique identifier for the wallet.
        user (User): One-to-one relationship with the User model.
        created_at (DateTime): Timestamp indicating when the wallet was created.
        updated_at (DateTime): Timestamp indicating when the wallet was last updated.

    """

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="wallet")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of -> {self.user.user_email}"


class ActivityTracker(models.Model):
    """
    Model representing activity tracking in the Wallet Manager.

    Attributes:
        TRANSACTION_CHOICES (list): Choices for the transaction type field.
        transaction_type (str): Type of the transaction.
        amount (Decimal): Amount involved in the transaction.
        description (str): Description of the transaction.
        created_at (DateTime): Timestamp indicating when the activity was tracked.
        user (User): Foreign key relationship with the User model.

    """

    TRANSACTION_CHOICES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    def __str__(self):
        return f"Activity Tracker of -> {self.user.user_email}"
