from rest_framework import serializers
from .models import Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["label", "balance"]
        read_only_fields = ["balance"]


class TransactionSerializer(serializers.ModelSerializer):
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())

    class Meta:
        model = Transaction
        fields = ["wallet", "txid", "amount"]
        read_only_fields = ["wallet"]
