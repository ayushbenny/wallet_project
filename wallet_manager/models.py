import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

from .regexp_validators import NameValidator, PhoneNumberValidator


class User(AbstractUser):
    first_name = models.CharField(
        max_length=50, null=False, blank=False, validators=[NameValidator.validate_name]
    )
    last_name = models.CharField(
        max_length=50, null=False, blank=False, validators=[NameValidator.validate_name]
    )
    user_email = models.EmailField(unique=True)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=15, validators=[PhoneNumberValidator.validate_phone_number])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User -> {self.user_email}"


class Wallet(models.Model):
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="wallet")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of -> {self.user.user_email}"


class ActivityTracker(models.Model):
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
