from decimal import Decimal

from django.db import models


class Wallet(models.Model):
    label = models.CharField(max_length=255)
    balance = models.DecimalField(
        max_digits=24, decimal_places=18, default=Decimal("0.000000000000000000")
    )

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(balance__gte=0), name="balance_gte_0")
        ]


class Transaction(models.Model):
    wallet = models.ForeignKey(
        Wallet, related_name="transactions", on_delete=models.PROTECT, db_index=True
    )
    txid = models.CharField(max_length=255, unique=True, db_index=True)
    amount = models.DecimalField(
        max_digits=24, decimal_places=18, default=Decimal("0.00")
    )
