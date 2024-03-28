"""Wallet Manger Views"""

from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .decorators import create_activity_tracker
from .models import ActivityTracker, User, Wallet
from .serializers import ActivityTrackerSerializer, UserSerializer, WalletSerializer
from rest_framework.permissions import AllowAny


class RegisterUserAPIView(APIView):
    """
    Endpoint for Registering a new User.

    This endpoint allows the  users to register into the system by providing their details.
    Upon successful user creation a new Wallet will be assigned to the same user with 0 amount as balance.
    If the input data is not as in the expected format, then it will throw error as well.

    Accepts a POST request with the following JSON payload:
    {
        "first_name": "string",
        "last_name": "string",
        "username": "string",
        "user_email": "string",
        "password": "string",
        "phone_number": "string"
    }
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            wallet_obj = Wallet.objects.create(user=user)
            wallet_serializer = WalletSerializer(wallet_obj)
            response_date = dict(user=serializer.data, wallet=wallet_serializer.data)
            return Response(response_date, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletAPIView(APIView):
    """
    Endpoint for creating a wallet for a user.

    This endpoint allows to create a new wallet for the specified user with a balance of 0.
    If the corresponding user is not found means then Error will be thrown.

    Accepts a POST request with the following JSON payload:
    {
        "user_id": int
    }
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        request_body = request.data
        user_id = request_body.get("user_id", None)
        if user_id:
            wallet_obj = Wallet.objects.create(user_id=user_id)
            wallet_serializer = WalletSerializer(wallet_obj)
            return Response(wallet_serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"message": "User not Found!"}, status=status.HTTP_400_BAD_REQUEST
        )


class WalletDepositAPIView(APIView):
    """
    Endpoint for deposting funds into the Users wallet.

    GET method:
    Retrives the current balance of the User

    POST method:
    In this method, Fund will be deposited to the corresponding user and the activity will be stored in the Activity Tracker.
    If the user is not found means then, Error will be thrown as well.

    Accepts a POST request with the following JSON payload:
    {
        "balance": amount_to_deposit
    }
    """

    def get(self, request, *args, **kwargs):
        user_params = request.user
        wallet_obj = get_object_or_404(Wallet, user_id=user_params.id)
        if wallet_obj:
            wallet_serializer = WalletSerializer(wallet_obj)
            return Response(wallet_serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    @create_activity_tracker(
        transaction_type="deposit",
        description_func=lambda user, amount: f"{user.username} deposited {amount} into wallet",
    )
    def post(self, request, *args, **kwargs):
        request_body = request.data
        wallet_obj = get_object_or_404(Wallet, user_id=request.user.id)
        if wallet_obj:
            wallet_balance = wallet_obj.balance
            new_wallet_balance = request_body.get("balance", None) + wallet_balance
            wallet_obj.balance = new_wallet_balance
            wallet_obj.save()
            wallet_serializer = WalletSerializer(wallet_obj)
            return Response(wallet_serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)


class WalletWithdrawAPIView(APIView):
    """
    Endpoint for withdrawing amount from user's wallet.

    In this method, the user will be withdrawing particular amount of fund from the wallet.
    After the successful withdrawal from the wallet, the record will be added into the Activity Tracker.
    If the user tries to withdraw amount greater than the amount that is available in the wallet means then, it will throw error

    Accepts a POST request with the following JSON payload:
    {
        "withdraw_amount": amount_to_withdraw
    }
    """

    @transaction.atomic
    @create_activity_tracker(
        transaction_type="withdrawal",
        description_func=lambda user, amount: f"{user.username} withdrawn {amount} from wallet",
    )
    def post(self, request, *args, **kwargs):
        request_body = request.data
        user = request.user
        withdraw_amount = request_body.get("withdraw_amount", None)
        wallet_obj = get_object_or_404(Wallet, user_id=user.id)
        available_balance = wallet_obj.balance
        if withdraw_amount <= available_balance:
            new_balance = available_balance - withdraw_amount
            wallet_obj.balance = new_balance
            wallet_obj.save()
            wallet_serializer = WalletSerializer(wallet_obj)
            return Response(wallet_serializer.data)
        return Response(
            {"message": "Insufficient Balance"}, status=status.HTTP_400_BAD_REQUEST
        )


class ActivityTrackerAPIView(APIView):
    """Endpoint to retrieve the Activity Tracker (History) of a particular user.

    In this method, the functionality will return the activity log or history of transcations which includes
    Deposit, Withdrawal and Transfer.

    The filtering process is as follows:
    transcation_type -> it will filter based on the Transcation type (for eg: deposit, withdrawal and transfer)
    from_date -> it will filter data starting from the date that is given
    to_date -> it will filter data till the date that is given

    It will only filter data only if a record of the requested user is present in the database.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        transaction_type_params = request.GET.get("transcation_type", None)
        from_date = request.GET.get("from_date", None)
        to_date = request.GET.get("to_date", None)
        query = ActivityTracker.objects.filter(
            user_id=user.id,
        )
        if query:
            if transaction_type_params:
                query = query.filter(transaction_type=transaction_type_params)
            if from_date:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
                query = query.filter(created_at__date__gte=from_date_obj.date())
            if to_date:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
                query = query.filter(created_at__date__lte=to_date_obj.date())
            activity_tracker_objs = query.all()
            activity_tracker_serializer = ActivityTrackerSerializer(
                activity_tracker_objs, many=True
            )
            return Response(activity_tracker_serializer.data)
        return Response(
            {"message": "User has no record in System"},
            status=status.HTTP_404_NOT_FOUND,
        )


class TranserFundAPIView(APIView):
    """
    Endpoint to transfer the fund from one user to another user how should be present in the system.

    There are multiple conditions that will be checked like whether the receiver is present in the system or not,
    transfer amount is valid or not, balance check for the sending user and so on

    Accepts a POST request with the following JSON payload:
    {
        "receiver_id": receiver_email,
        "transfer_amount": transfer amount
    }
    """

    @transaction.atomic
    @create_activity_tracker(
        transaction_type="transfer",
        description_func=lambda user, amount, receiver: f"{amount} has been transfered from {user.username} to {receiver}",
    )
    def post(self, request, *args, **kwargs):
        request_body = request.data
        sender_id = request.user
        receiver_id = request_body.get("receiver_id", None)
        transfer_amount = request_body.get("transfer_amount", None)
        if transfer_amount <= 0:
            return Response(
                {"message": "Transfer amount must be greater than zero."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        receiver_check = get_object_or_404(User, user_email=receiver_id)
        if request.user != receiver_check:
            if receiver_check:
                sender_wallet_obj = get_object_or_404(Wallet, user_id=sender_id)
                wallet_balance_amount = sender_wallet_obj.balance
                if transfer_amount <= wallet_balance_amount:
                    receiver_wallet_obj = get_object_or_404(
                        Wallet, user_id=receiver_check
                    )
                    new_receiver_balance = receiver_wallet_obj.balance + transfer_amount
                    receiver_wallet_obj.balance = new_receiver_balance
                    receiver_wallet_obj.save()
                    new_sender_balance = wallet_balance_amount - transfer_amount
                    sender_wallet_obj.balance = new_sender_balance
                    sender_wallet_obj.save()
                    return Response(
                        {
                            "message": f"Amount has been successfully transfered to {receiver_check.username}"
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"message": "Insufficient Balance. Please add fund to the Wallet"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "User has no record in System"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"message": "Cannot transfer Funds to the same User"},
            status=status.HTTP_400_BAD_REQUEST,
        )
