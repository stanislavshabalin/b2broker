from decimal import Decimal

from django.db import transaction as db_transaction
from django.db.models import F

from rest_framework import serializers
from rest_framework.filters import SearchFilter
from rest_framework_json_api import filters, django_filters
from rest_framework_json_api.views import ModelViewSet

from .models import Transaction, Wallet
from .serializers import TransactionSerializer, WalletSerializer


class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    filter_backends = [
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = {
        "label": ["iexact", "icontains"],
        "balance": ["exact", "lte", "gte"],
    }
    search_fields = ["label", "balance"]


class TransactionViewSet(ModelViewSet):
    serializer_class = TransactionSerializer

    filter_backends = [
        filters.OrderingFilter,
        django_filters.DjangoFilterBackend,
        SearchFilter,
    ]

    filterset_fields = {
        "txid": ["exact"],
        "amount": ["exact", "lte", "gte"],
    }
    search_fields = ["label", "balance"]

    def get_queryset(self):
        return Transaction.objects.filter(wallet=self.kwargs["wallet_pk"])

    def perform_create(self, serializer):
        with db_transaction.atomic():
            wallet_transaction = serializer.save()
            wallet = wallet_transaction.wallet
            if wallet.balance + wallet_transaction.amount < Decimal("0"):
                raise serializers.ValidationError("Wallet balance must be positive.")

            wallet.balance = F("balance") + wallet_transaction.amount
            wallet.save()
