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
