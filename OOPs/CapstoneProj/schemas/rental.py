from datetime import date, timedelta

from .exceptions import InvalidRentalPeriodError, RentalStateError
from .invoice import Invoice


class Rental:
    """One rental transaction; composes Customer, Vehicle, Payment and Invoice."""

    LATE_FEE_RATE = 0.20

    def __init__(self, rental_id, customer, vehicle, days, start_date):
        if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
            raise InvalidRentalPeriodError("Rental days must be greater than zero.")
        if not isinstance(start_date, date):
            raise InvalidRentalPeriodError("Start date must be a valid date.")

        self.__rental_id = str(rental_id)
        self.__customer = customer
        self.__vehicle = vehicle
        self.__days = days
        self.__start_date = start_date
        self.__expected_return_date = start_date + timedelta(days=days)
        self.__actual_return_date = None
        self.__base_amount = vehicle.calculate_rental_cost(days)
        self.__late_fee = 0.0
        self.__final_amount = self.__base_amount
        self.__status = "ACTIVE"
        self.__payment_result = None
        self.__invoice = None

    @property
    def rental_id(self):
        return self.__rental_id

    @property
    def customer(self):
        return self.__customer

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def days(self):
        return self.__days

    @property
    def rental_days(self):
        return self.__days

    @property
    def start_date(self):
        return self.__start_date

    @property
    def expected_return_date(self):
        return self.__expected_return_date

    @property
    def actual_return_date(self):
        return self.__actual_return_date

    @property
    def base_amount(self):
        return self.__base_amount

    @property
    def late_fee(self):
        return self.__late_fee

    @property
    def final_amount(self):
        return self.__final_amount

    @property
    def status(self):
        return self.__status

    @property
    def payment_result(self):
        return self.__payment_result

    @property
    def invoice(self):
        return self.__invoice

    def attach_payment(self, payment_result):
        if not payment_result.success:
            raise RentalStateError("A rental cannot be confirmed after failed payment.")
        self.__payment_result = payment_result

    def complete_rental(self, actual_return_date):
        if self.__status != "ACTIVE":
            raise RentalStateError("This rental has already been completed.")
        if not isinstance(actual_return_date, date):
            raise RentalStateError("Return date must be a valid date.")
        if actual_return_date < self.start_date:
            raise RentalStateError("Return date cannot be before the rental start date.")

        self.__actual_return_date = actual_return_date
        late_days = max(0, (actual_return_date - self.expected_return_date).days)
        self.__late_fee = late_days * (self.LATE_FEE_RATE * self.vehicle.daily_rate)
        self.__final_amount = self.__base_amount + self.__late_fee
        self.__status = "COMPLETED"
        self.__invoice = Invoice(self)
        return self.__invoice

    def __str__(self):
        return (
            f"{self.rental_id} | {self.vehicle.vehicle_type} {self.vehicle.vehicle_id} | "
            f"{self.start_date} -> {self.actual_return_date or self.expected_return_date} | "
            f"Rs. {self.final_amount:,.2f} | {self.status}"
        )
