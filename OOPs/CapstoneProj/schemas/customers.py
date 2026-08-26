import re

from .exceptions import ValidationError


class Customer:
    """Customer domain object with encapsulated personal data and rental history."""

    def __init__(self, customer_id, name, email, driving_license_number):
        self.__customer_id = self._required(customer_id, "Customer ID")
        self.__name = self._required(name, "Name")
        self.__email = self._required(email, "Email")
        self.validate_email(self.__email)
        self.__driving_license_number = self._required(
            driving_license_number, "Driving License Number"
        )
        self.__rental_history = []

    @staticmethod
    def _required(value, field_name):
        if value is None or not str(value).strip():
            raise ValidationError(f"{field_name} is required.")
        return str(value).strip()

    @staticmethod
    def validate_email(email):
        pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format.")

    @property
    def customer_id(self):
        return self.__customer_id

    @property
    def name(self):
        return self.__name

    @property
    def email(self):
        return self.__email

    @property
    def driving_license_number(self):
        return self.__driving_license_number

    @property
    def rental_history(self):
        return tuple(self.__rental_history)

    def add_rental(self, rental):
        if rental not in self.__rental_history:
            self.__rental_history.append(rental)

    def display_rental_history(self):
        if not self.__rental_history:
            return "No rental history available."
        return "\n".join(str(rental) for rental in self.__rental_history)

    def __str__(self):
        return (
            f"{self.customer_id} | {self.name} | {self.email} | "
            f"Licence: {self.driving_license_number}"
        )
