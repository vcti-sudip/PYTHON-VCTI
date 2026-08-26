from abc import ABC, abstractmethod

from .exceptions import ValidationError


class Vehicle(ABC):
    """Abstract base class for all rentable vehicles."""

    def __init__(self, vehicle_id, registration_number, brand, model, daily_rate, available=True):
        self.__vehicle_id = self._required(vehicle_id, "Vehicle ID")
        self.__registration_number = self._required(registration_number, "Registration Number")
        self.__brand = self._required(brand, "Brand")
        self.__model = self._required(model, "Model")
        self.__daily_rate = self._positive_number(daily_rate, "Daily rental rate")
        if not isinstance(available, bool):
            raise ValidationError("Availability status must be True or False.")
        self.__available = available

    @staticmethod
    def _required(value, field_name):
        if value is None or not str(value).strip():
            raise ValidationError(f"{field_name} is required.")
        return str(value).strip()

    @staticmethod
    def _positive_number(value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValidationError(f"{field_name} must be a positive number.")
        return float(value)

    @property
    def vehicle_id(self):
        return self.__vehicle_id

    @property
    def registration_number(self):
        return self.__registration_number

    @property
    def brand(self):
        return self.__brand

    @property
    def model(self):
        return self.__model

    @property
    def daily_rate(self):
        return self.__daily_rate

    @property
    def rental_price_per_day(self):
        """Backward-compatible alias for the original project field name."""
        return self.__daily_rate

    def mark_as_available(self):
        self.__available = True

    def mark_as_rented(self):
        self.__available = False

    def is_available(self):
        return self.__available

    @property
    @abstractmethod
    def vehicle_type(self):
        """Return the concrete vehicle type."""

    @abstractmethod
    def calculate_rental_cost(self, rental_days):
        """Calculate rental cost using the vehicle-specific business rule."""

    def display_details(self):
        status = "Available" if self.is_available() else "Rented"
        return (
            f"{self.vehicle_id:<10} | {self.vehicle_type:<4} | {self.brand:<16} | "
            f"{self.model:<18} | Rs. {self.daily_rate:,.2f}/day | {status}"
        )

    def __str__(self):
        return self.display_details()


class Car(Vehicle):
    @property
    def vehicle_type(self):
        return "Car"

    def calculate_rental_cost(self, rental_days):
        self._validate_rental_days(rental_days)
        return self.daily_rate * rental_days

    @staticmethod
    def _validate_rental_days(rental_days):
        if not isinstance(rental_days, int) or isinstance(rental_days, bool) or rental_days <= 0:
            raise ValidationError("Rental days must be a positive integer.")


class Bike(Vehicle):
    @property
    def vehicle_type(self):
        return "Bike"

    def calculate_rental_cost(self, rental_days):
        if not isinstance(rental_days, int) or isinstance(rental_days, bool) or rental_days <= 0:
            raise ValidationError("Rental days must be a positive integer.")
        amount = self.daily_rate * rental_days
        if rental_days > 5:
            amount *= 0.95
        return amount


class Van(Vehicle):
    def __init__(self, vehicle_id, registration_number, brand, model, daily_rate, service_charge=500, available=True):
        super().__init__(vehicle_id, registration_number, brand, model, daily_rate, available)
        if isinstance(service_charge, bool) or not isinstance(service_charge, (int, float)) or service_charge < 0:
            raise ValidationError("Service charge must be zero or a positive number.")
        self.__service_charge = float(service_charge)

    @property
    def vehicle_type(self):
        return "Van"

    @property
    def service_charge(self):
        return self.__service_charge

    def calculate_rental_cost(self, rental_days):
        if not isinstance(rental_days, int) or isinstance(rental_days, bool) or rental_days <= 0:
            raise ValidationError("Rental days must be a positive integer.")
        return (self.daily_rate * rental_days) + self.service_charge
