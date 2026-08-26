import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from schemas.customers import Customer
from schemas.exceptions import (
    InvalidRentalPeriodError,
    PaymentProcessingError,
    VehicleNotAvailableError,
)
from schemas.payment import CardPayment, UPIPayment
from schemas.vehicles import Bike, Car, Van
from services.rental_service import RentalService


class RentalSystemTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        for name, data in (
            ("customers.json", []),
            ("vehicles.json", []),
            ("rents.json", []),
        ):
            (self.data_dir / name).write_text(json.dumps(data), encoding="utf-8")

        self.service = RentalService(self.data_dir)
        self.customer_a = Customer("C1", "Ananya", "ananya@example.com", "DL1")
        self.customer_b = Customer("C2", "Rahul", "rahul@example.com", "DL2")
        self.service.register_customer(self.customer_a, persist=False)
        self.service.register_customer(self.customer_b, persist=False)
        self.service.add_vehicle(Car("V1", "REG1", "Toyota", "Camry", 2000), persist=False)
        self.service.add_vehicle(Bike("V2", "REG2", "Yamaha", "MT-15", 700), persist=False)
        self.service.add_vehicle(Van("V3", "REG3", "Tata", "Winger", 3000, 500), persist=False)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_polymorphic_vehicle_pricing(self):
        self.assertEqual(self.service.get_vehicle("V1").calculate_rental_cost(3), 6000)
        self.assertEqual(self.service.get_vehicle("V2").calculate_rental_cost(5), 3500)
        self.assertEqual(self.service.get_vehicle("V2").calculate_rental_cost(6), 3990)
        self.assertEqual(self.service.get_vehicle("V3").calculate_rental_cost(3), 9500)

    def test_payment_methods_accept_numeric_selection(self):
        card = CardPayment()
        upi = UPIPayment()
        self.assertEqual(card.process_payment(100).method, "Card")
        self.assertEqual(upi.process_payment(100).method, "UPI")

    def test_invalid_rental_days(self):
        with self.assertRaises(InvalidRentalPeriodError):
            self.service.rent_vehicle("C1", "V1", 0, CardPayment())

    def test_failed_payment_does_not_confirm_rental(self):
        with self.assertRaises(PaymentProcessingError):
            self.service.rent_vehicle("C1", "V1", 3, CardPayment(simulate_failure=True))
        self.assertTrue(self.service.get_vehicle("V1").is_available())
        self.assertEqual(len(self.service.rentals), 0)

    def test_unavailable_vehicle_is_rejected(self):
        rental = self.service.rent_vehicle("C1", "V1", 3, CardPayment())
        self.assertEqual(rental.status, "ACTIVE")
        with self.assertRaises(VehicleNotAvailableError):
            self.service.rent_vehicle("C2", "V1", 2, UPIPayment())

    def test_late_fee_and_return(self):
        rental = self.service.rent_vehicle("C1", "V1", 3, CardPayment())
        invoice = self.service.return_vehicle(
            rental.rental_id, rental.expected_return_date + timedelta(days=1)
        )
        self.assertEqual(rental.late_fee, 400)
        self.assertEqual(rental.final_amount, 6400)
        self.assertEqual(invoice.generate()["final_amount"], 6400)
        self.assertTrue(self.service.get_vehicle("V1").is_available())

    def test_json_persistence(self):
        rental = self.service.rent_vehicle("C1", "V1", 3, UPIPayment())
        self.service.return_vehicle(rental.rental_id, date.today())

        persisted = json.loads((self.data_dir / "rents.json").read_text(encoding="utf-8"))
        self.assertEqual(len(persisted), 1)
        self.assertEqual(persisted[0]["status"], "COMPLETED")
        self.assertIn("payment", persisted[0])
        self.assertNotIn("card_number", persisted[0])
        self.assertNotIn("cvv", persisted[0])

        reloaded = RentalService(self.data_dir)
        reloaded.load_data()
        self.assertEqual(len(reloaded.rentals), 1)
        self.assertEqual(reloaded.get_rental(rental.rental_id).status, "COMPLETED")
        self.assertTrue(reloaded.get_vehicle("V1").is_available())


if __name__ == "__main__":
    unittest.main()
