from django.urls import path, include
from rest_framework_nested import routers

from .views import WalletViewSet, TransactionViewSet

wallets_router = routers.SimpleRouter()
wallets_router.register("wallets", WalletViewSet, basename="wallet")

wallet_transactions_router = routers.NestedSimpleRouter(
    wallets_router, "wallets", lookup="wallet"
)
wallet_transactions_router.register(
    "transactions", TransactionViewSet, basename="wallet-transaction"
)

urlpatterns = [
    path(r"", include(wallets_router.urls)),
    path(r"", include(wallet_transactions_router.urls)),
]
