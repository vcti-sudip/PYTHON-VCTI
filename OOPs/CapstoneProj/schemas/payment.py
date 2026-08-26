from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class PaymentResult:
    success: bool
    transaction_id: str
    method: str
    amount: float
    message: str


class PaymentProcessor(ABC):
    """Payment contract used by RentalService (dependency inversion)."""

    @abstractmethod
    def process_payment(self, amount):
        """Process a payment and return a PaymentResult."""


class CardPayment(PaymentProcessor):
    def __init__(self, simulate_failure=False):
        self.__simulate_failure = simulate_failure

    def process_payment(self, amount):
        if amount <= 0:
            return PaymentResult(False, "", "Card", amount, "Amount must be positive.")
        if self.__simulate_failure:
            return PaymentResult(False, "", "Card", amount, "Card payment declined (simulated).")
        return PaymentResult(
            True,
            f"CARD-{uuid4().hex[:8].upper()}",
            "Card",
            float(amount),
            "Payment completed successfully.",
        )


class UPIPayment(PaymentProcessor):
    def __init__(self, simulate_failure=False):
        self.__simulate_failure = simulate_failure

    def process_payment(self, amount):
        if amount <= 0:
            return PaymentResult(False, "", "UPI", amount, "Amount must be positive.")
        if self.__simulate_failure:
            return PaymentResult(False, "", "UPI", amount, "UPI payment failed (simulated).")
        return PaymentResult(
            True,
            f"UPI-{uuid4().hex[:8].upper()}",
            "UPI",
            float(amount),
            "Payment completed successfully.",
        )
