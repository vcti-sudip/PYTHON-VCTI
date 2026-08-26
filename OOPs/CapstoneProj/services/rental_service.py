from datetime import date
from pathlib import Path
import json

from schemas.exceptions import (
    CustomerNotFoundError,
    InvalidRentalPeriodError,
    PaymentProcessingError,
    RentalStateError,
    ValidationError,
    VehicleNotAvailableError,
    VehicleNotFoundError,
)
from schemas.rental import Rental


class RentalService:
    """Application service coordinating vehicles, customers and rental transactions."""

    def __init__(self, data_dir=None):
        self.__vehicles = {}
        self.__customers = {}
        self.__rentals = {}
        self.__data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
        self.__vehicles_file = self.__data_dir / "vehicles.json"
        self.__customers_file = self.__data_dir / "customers.json"
        self.__rentals_file = self.__data_dir / "rents.json"

    @property
    def vehicles(self):
        return tuple(self.__vehicles.values())

    @property
    def customers(self):
        return tuple(self.__customers.values())

    @property
    def rentals(self):
        return tuple(self.__rentals.values())

    def add_vehicle(self, vehicle, persist=True):
        if vehicle.vehicle_id in self.__vehicles:
            raise ValidationError(f"Vehicle with ID {vehicle.vehicle_id} already exists.")
        self.__vehicles[vehicle.vehicle_id] = vehicle
        if persist:
            self.save_data()

    def register_customer(self, customer, persist=True):
        if customer.customer_id in self.__customers:
            raise ValidationError(f"Customer with ID {customer.customer_id} already exists.")
        self.__customers[customer.customer_id] = customer
        if persist:
            self.save_data()

    def get_vehicle(self, vehicle_id):
        vehicle = self.__vehicles.get(vehicle_id)
        if not vehicle:
            raise VehicleNotFoundError(f"Vehicle with ID {vehicle_id} not found.")
        return vehicle

    def get_customer(self, customer_id):
        customer = self.__customers.get(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"Customer with ID {customer_id} not found.")
        return customer

    def get_rental(self, rental_id):
        rental = self.__rentals.get(rental_id)
        if not rental:
            raise RentalStateError(f"Rental with ID {rental_id} not found.")
        return rental

    def display_available_vehicles(self):
        available = [v for v in self.__vehicles.values() if v.is_available()]
        if not available:
            return "No vehicles are currently available."
        lines = ["ID         | Type | Brand            | Model              | Rate            | Status",
                 "-" * 87]
        lines.extend(v.display_details() for v in available)
        return "\n".join(lines)

    def search(self, vehicle_id=None, vehicle_type=None, min_price=None, max_price=None):
        """Flexible search equivalent to overloaded search methods in Python."""
        results = list(self.__vehicles.values())
        if vehicle_id:
            results = [v for v in results if v.vehicle_id.lower() == vehicle_id.lower()]
        if vehicle_type:
            results = [v for v in results if v.vehicle_type.lower() == vehicle_type.lower()]
        if min_price is not None:
            results = [v for v in results if v.daily_rate >= float(min_price)]
        if max_price is not None:
            results = [v for v in results if v.daily_rate <= float(max_price)]
        return results

    def rent_vehicle(self, customer_id, vehicle_id, days, payment_processor, start_date=None):
        if not isinstance(days, int) or isinstance(days, bool) or days <= 0:
            raise InvalidRentalPeriodError("Rental days must be greater than zero.")

        customer = self.get_customer(customer_id)
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle.is_available():
            raise VehicleNotAvailableError(f"Vehicle {vehicle_id} is not available for rent.")

        rental_date = start_date or date.today()
        rental_id = self._next_rental_id()
        rental = Rental(rental_id, customer, vehicle, days, rental_date)
        payment_result = payment_processor.process_payment(rental.base_amount)
        if not payment_result.success:
            raise PaymentProcessingError(payment_result.message)

        rental.attach_payment(payment_result)
        vehicle.mark_as_rented()
        customer.add_rental(rental)
        self.__rentals[rental_id] = rental
        self.save_data()
        return rental

    def return_vehicle(self, rental_id, return_date=None):
        rental = self.get_rental(rental_id)
        if rental.status != "ACTIVE":
            raise RentalStateError(f"Rental {rental_id} is not active.")
        invoice = rental.complete_rental(return_date or date.today())
        rental.vehicle.mark_as_available()
        self.save_data()
        return invoice

    def add_existing_rental(self, rental):
        self.__rentals[rental.rental_id] = rental
        rental.customer.add_rental(rental)

    def load_data(self):
        self.__data_dir.mkdir(parents=True, exist_ok=True)
        self._load_customers()
        self._load_vehicles()
        self._load_rentals()

    def save_data(self):
        self.__data_dir.mkdir(parents=True, exist_ok=True)
        self._save_customers()
        self._save_vehicles()
        self._save_rentals()

    def _load_customers(self):
        self.__customers.clear()
        if not self.__customers_file.exists() or self.__customers_file.stat().st_size == 0:
            return
        records = self._read_json(self.__customers_file, [])
        from schemas.customers import Customer
        for data in records:
            customer = Customer(
                data["customer_id"], data["name"], data["email"], data["driving_license_number"]
            )
            self.__customers[customer.customer_id] = customer

    def _load_vehicles(self):
        self.__vehicles.clear()
        if not self.__vehicles_file.exists() or self.__vehicles_file.stat().st_size == 0:
            return
        records = self._read_json(self.__vehicles_file, [])
        from schemas.vehicles import Car, Bike, Van
        classes = {"Car": Car, "Bike": Bike, "Van": Van}
        for data in records:
            vehicle_type = data.get("type", "Car")
            cls = classes.get(vehicle_type)
            if cls is None:
                raise ValidationError(f"Unsupported vehicle type: {vehicle_type}")
            common = dict(
                vehicle_id=data["vehicle_id"],
                registration_number=data["registration_number"],
                brand=data["brand"],
                model=data["model"],
                daily_rate=data.get("daily_rate", data.get("rental_price_per_day")),
                available=data.get("available", data.get("availability_status", True)),
            )
            if cls is Van:
                common["service_charge"] = data.get("service_charge", 500)
            vehicle = cls(**common)
            self.__vehicles[vehicle.vehicle_id] = vehicle

    def _load_rentals(self):
        self.__rentals.clear()
        if not self.__rentals_file.exists() or self.__rentals_file.stat().st_size == 0:
            return
        records = self._read_json(self.__rentals_file, [])
        for data in records:
            try:
                customer = self.get_customer(data["customer_id"])
                vehicle = self.get_vehicle(data["vehicle_id"])
            except (CustomerNotFoundError, VehicleNotFoundError):
                continue
            rental = Rental(
                data["rental_id"],
                customer,
                vehicle,
                int(data["days"]),
                date.fromisoformat(data["start_date"]),
            )
            payment = data.get("payment") or {}
            if payment.get("success"):
                from schemas.payment import PaymentResult
                rental.attach_payment(
                    PaymentResult(
                        True,
                        payment.get("transaction_id", ""),
                        payment.get("method", ""),
                        float(payment.get("amount", rental.base_amount)),
                        payment.get("message", "Payment completed successfully."),
                    )
                )
            actual_return = data.get("actual_return_date")
            if actual_return:
                rental.complete_rental(date.fromisoformat(actual_return))
            self.__rentals[rental.rental_id] = rental
            customer.add_rental(rental)

    @staticmethod
    def _read_json(path, default):
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Invalid JSON in {path.name}: {exc}") from exc

    def _save_customers(self):
        payload = [
            {
                "customer_id": c.customer_id,
                "name": c.name,
                "email": c.email,
                "driving_license_number": c.driving_license_number,
            }
            for c in self.__customers.values()
        ]
        self._write_json(self.__customers_file, payload)

    def _save_vehicles(self):
        payload = []
        for v in self.__vehicles.values():
            data = {
                "vehicle_id": v.vehicle_id,
                "type": v.vehicle_type,
                "registration_number": v.registration_number,
                "brand": v.brand,
                "model": v.model,
                "daily_rate": v.daily_rate,
                "available": v.is_available(),
            }
            if v.vehicle_type == "Van":
                data["service_charge"] = v.service_charge
            payload.append(data)
        self._write_json(self.__vehicles_file, payload)

    def _save_rentals(self):
        payload = []
        for r in self.__rentals.values():
            payment = r.payment_result
            record = {
                "rental_id": r.rental_id,
                "customer_id": r.customer.customer_id,
                "vehicle_id": r.vehicle.vehicle_id,
                "start_date": r.start_date.isoformat(),
                "expected_return_date": r.expected_return_date.isoformat(),
                "actual_return_date": r.actual_return_date.isoformat() if r.actual_return_date else None,
                "days": r.days,
                "base_amount": round(r.base_amount, 2),
                "late_fee": round(r.late_fee, 2),
                "final_amount": round(r.final_amount, 2),
                "status": r.status,
                "payment": {
                    "success": payment.success,
                    "transaction_id": payment.transaction_id,
                    "method": payment.method,
                    "amount": round(payment.amount, 2),
                    "message": payment.message,
                } if payment else None,
            }
            payload.append(record)
        self._write_json(self.__rentals_file, payload)

    @staticmethod
    def _write_json(path, payload):
        temp_path = path.with_suffix(path.suffix + ".tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)
        temp_path.replace(path)

    def _next_rental_id(self):
        numbers = []
        for rental_id in self.__rentals:
            if rental_id.startswith("R") and rental_id[1:].isdigit():
                numbers.append(int(rental_id[1:]))
        next_number = max(numbers, default=0) + 1
        return f"R{next_number:04d}"
