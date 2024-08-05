import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("txid", models.CharField(db_index=True, max_length=255, unique=True)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=18, default=Decimal("0.00"), max_digits=24
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Wallet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=255)),
                (
                    "balance",
                    models.DecimalField(
                        decimal_places=18, default=Decimal("0.00"), max_digits=24
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="wallet",
            constraint=models.CheckConstraint(
                check=models.Q(("balance__gte", 0)), name="balance_gte_0"
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="wallet",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="transactions",
                to="testapp.wallet",
            ),
        ),
    ]
