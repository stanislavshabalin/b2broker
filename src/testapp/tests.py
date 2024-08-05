import pytest
from decimal import Decimal

from django.urls import reverse

from testapp.models import Wallet, Transaction


@pytest.fixture
def wallet():
    return Wallet.objects.create(label="wallet_label")


@pytest.fixture
def transaction(wallet):
    return Transaction.objects.create(
        wallet=wallet, txid="42", amount=Decimal("0.000000000000012345")
    )


@pytest.mark.django_db
def test_empty_wallet(api_client):
    result = api_client.get(reverse("api:wallet-list"))

    assert result.status_code == 200
    assert len(result.json()["data"]) == 0


@pytest.mark.django_db
def test_create_wallet_api(api_client):
    WALLET_LABEL = "wallet_label"
    WALLET_ZERO_BALANCE = "0.000000000000000000"

    payload = {"data": {"type": "Wallet", "attributes": {"label": WALLET_LABEL}}}
    result = api_client.post(reverse("api:wallet-list"), data=payload)

    assert result.status_code == 201
    data = result.json()["data"]
    assert data["attributes"]["label"] == WALLET_LABEL
    assert data["attributes"]["balance"] == WALLET_ZERO_BALANCE


@pytest.mark.django_db
def test_get_wallet(api_client, wallet):
    result = api_client.get(reverse("api:wallet-detail", kwargs={"pk": wallet.id}))
    data = result.json()["data"]
    assert data["attributes"]["label"] == wallet.label
    assert Decimal(data["attributes"]["balance"]) == wallet.balance


@pytest.mark.django_db
def test_wallets_list(api_client, wallet):
    result = api_client.get(reverse("api:wallet-list"))
    assert result.status_code == 200
    json_data = result.json()["data"]
    assert len(json_data) == 1
    assert json_data[0]["attributes"]["label"] == wallet.label


@pytest.mark.django_db
def test_no_transactions(api_client, wallet):
    result = api_client.get(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": wallet.pk})
    )

    assert result.status_code == 200
    assert len(result.json()["data"]) == 0


@pytest.mark.django_db
def test_create_transaction(api_client, wallet):
    TRANSACTION_TXID = "42"
    TRANSACTION_AMOUNT = "0.000000000000012345"

    payload = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "wallet": wallet.pk,
                "txid": TRANSACTION_TXID,
                "amount": TRANSACTION_AMOUNT,
            },
        },
    }
    result = api_client.post(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": wallet.pk}),
        data=payload,
    )

    assert result.status_code == 201
    data = result.json()["data"]
    assert data["attributes"]["txid"] == TRANSACTION_TXID
    assert data["attributes"]["amount"] == TRANSACTION_AMOUNT


@pytest.mark.django_db
def test_get_transaction(api_client, transaction):
    result = api_client.get(
        reverse(
            "api:wallet-transaction-detail",
            kwargs={"wallet_pk": transaction.wallet.pk, "pk": transaction.id},
        )
    )
    data = result.json()["data"]
    assert data["attributes"]["txid"] == transaction.txid
    assert Decimal(data["attributes"]["amount"]) == transaction.amount


@pytest.mark.django_db
def test_transactions_list(api_client, transaction):
    result = api_client.get(
        reverse(
            "api:wallet-transaction-list", kwargs={"wallet_pk": transaction.wallet.pk}
        )
    )
    assert result.status_code == 200
    json_data = result.json()["data"]
    assert len(json_data) == 1
    assert json_data[0]["attributes"]["txid"] == transaction.txid


@pytest.mark.django_db
def test_wallet_balance(api_client, wallet):
    TXID_1 = "42"
    AMOUNT_1 = "0.000000000000012345"
    TXID_2 = "43"
    AMOUNT_2 = "-0.000000000000000005"

    payload = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "wallet": wallet.pk,
                "txid": TXID_1,
                "amount": AMOUNT_1,
            },
        }
    }
    result = api_client.post(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": wallet.pk}),
        data=payload,
    )

    assert result.status_code == 201
    wallet.refresh_from_db()
    assert wallet.balance == Decimal(AMOUNT_1)

    payload = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "wallet": wallet.pk,
                "txid": TXID_2,
                "amount": AMOUNT_2,
            },
        }
    }
    result = api_client.post(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": wallet.pk}),
        data=payload,
    )

    assert result.status_code == 201

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("0.000000000000012340")


@pytest.mark.django_db
def test_wallet_negative_balance(api_client, wallet):
    TXID_1 = "42"
    AMOUNT_1 = "0.000000000000012345"
    TXID_2 = "43"
    AMOUNT_2 = "-0.00000000000012346"

    payload = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "wallet": wallet.pk,
                "txid": TXID_1,
                "amount": AMOUNT_1,
            },
        }
    }
    result = api_client.post(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": wallet.pk}),
        data=payload,
    )
    assert result.status_code == 201

    payload = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "wallet": wallet.pk,
                "txid": TXID_2,
                "amount": AMOUNT_2,
            },
        }
    }
    result = api_client.post(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": wallet.pk}),
        data=payload,
    )
    assert result.status_code == 400

    wallet.refresh_from_db()
    assert wallet.balance == Decimal(AMOUNT_1)


@pytest.mark.django_db
def test_transaction_to_wrong_wallet_id(api_client):
    payload = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "wallet": 404,
                "txid": "42",
                "amount": "0.000000000000012345",
            },
        }
    }
    result = api_client.post(
        reverse("api:wallet-transaction-list", kwargs={"wallet_pk": 404}),
        data=payload,
    )

    assert result.status_code == 400
    assert result.json()["errors"][0]["code"] == "does_not_exist"
