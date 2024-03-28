"""Decorators for Wallet Manager"""

from rest_framework import status

from .models import ActivityTracker, User


def create_activity_tracker(transaction_type, description_func):
    def decorator(func):
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if response.status_code == status.HTTP_200_OK:
                request = args[1]
                request_data = request.data
                receiver_id = request_data.get("receiver_id", None)
                amount = request_data.get(
                    "balance",
                    request_data.get(
                        "withdraw_amount", request_data.get("transfer_amount")
                    ),
                )
                user = request.user
                if receiver_id:
                    receiver_obj = User.objects.get(user_email=receiver_id)
                    description = description_func(user, amount, receiver_obj.username)
                else:
                    description = description_func(user, amount)
                ActivityTracker.objects.create(
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    user_id=user.id,
                )
            return response

        return wrapper

    return decorator
