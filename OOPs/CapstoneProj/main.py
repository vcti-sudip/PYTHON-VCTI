from datetime import date, timedelta
from pathlib import Path

from schemas.customers import Customer
from schemas.exceptions import RentalError, ValidationError
from schemas.payment import CardPayment, UPIPayment
from schemas.vehicles import Bike, Car, Van
from services.rental_service import RentalService


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"


def create_service():
    service = RentalService(DATA_DIR)
    service.load_data()
    return service


def seed_demo_records(service):
    """Ensure the exact mandatory-scenario records exist for a manager demo."""
    demo_customers = [
        Customer("DEMO001", "Ananya Sharma", "ananya.sharma@example.com", "DL-DEMO-001"),
        Customer("DEMO002", "Rahul Verma", "rahul.verma@example.com", "DL-DEMO-002"),
    ]
    for customer in demo_customers:
        if not any(c.customer_id == customer.customer_id for c in service.customers):
            service.register_customer(customer, persist=False)

    demo_vehicles = [
        Car("V101", "JH01DEMO1", "Toyota", "Camry", 2000, available=True),
        Bike("V102", "JH01DEMO2", "Yamaha", "MT-15", 700, available=True),
        Van("V103", "JH01DEMO3", "Tata", "Winger", 3000, service_charge=500, available=True),
    ]
    for vehicle in demo_vehicles:
        if not any(v.vehicle_id == vehicle.vehicle_id for v in service.vehicles):
            service.add_vehicle(vehicle, persist=False)
    service.save_data()


def print_header(title):
    print("\n" + "=" * 72)
    print(f"{title:^72}")
    print("=" * 72)


def list_vehicles(service, available_only=False):
    vehicles = [v for v in service.vehicles if v.is_available()] if available_only else list(service.vehicles)
    print_header("AVAILABLE VEHICLES" if available_only else "ALL VEHICLES")
    if not vehicles:
        print("No vehicles found.")
        return
    print("ID         Type | Brand            | Model              | Rate            | Status")
    print("-" * 88)
    for vehicle in vehicles:
        print(vehicle.display_details())


def list_customers(service):
    print_header("CUSTOMERS")
    if not service.customers:
        print("No customers registered.")
        return
    for customer in service.customers:
        print(customer)


def search_vehicles(service):
    print_header("SEARCH VEHICLES")
    vehicle_id = input("Vehicle ID (Enter to skip): ").strip() or None
    vehicle_type = input("Type [Car/Bike/Van] (Enter to skip): ").strip() or None
    min_price = input("Minimum daily rate (Enter to skip): ").strip()
    max_price = input("Maximum daily rate (Enter to skip): ").strip()

    try:
        results = service.search(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
            min_price=float(min_price) if min_price else None,
            max_price=float(max_price) if max_price else None,
        )
        if not results:
            print("No vehicles matched the search.")
            return
        for vehicle in results:
            print(vehicle.display_details())
    except ValueError:
        print("Invalid price. Please enter a numeric value.")


def register_customer(service):
    print_header("REGISTER CUSTOMER")
    try:
        customer = Customer(
            input("Customer ID: ").strip(),
            input("Name: ").strip(),
            input("Email: ").strip(),
            input("Driving licence number: ").strip(),
        )
        service.register_customer(customer)
        print("Customer registered successfully.")
    except RentalError as exc:
        print(f"Registration failed: {exc}")


def add_vehicle(service):
    print_header("ADD VEHICLE")
    try:
        vehicle_type = input("Vehicle type [Car/Bike/Van]: ").strip().title()
        vehicle_id = input("Vehicle ID: ").strip()
        registration = input("Registration number: ").strip()
        brand = input("Brand: ").strip()
        model = input("Model: ").strip()
        daily_rate = float(input("Daily rental rate: ").strip())

        if vehicle_type == "Car":
            vehicle = Car(vehicle_id, registration, brand, model, daily_rate)
        elif vehicle_type == "Bike":
            vehicle = Bike(vehicle_id, registration, brand, model, daily_rate)
        elif vehicle_type == "Van":
            service_charge = float(input("Service charge: ").strip())
            vehicle = Van(vehicle_id, registration, brand, model, daily_rate, service_charge)
        else:
            raise ValidationError("Vehicle type must be Car, Bike, or Van.")

        service.add_vehicle(vehicle)
        print("Vehicle added successfully.")
    except (RentalError, ValueError) as exc:
        print(f"Vehicle creation failed: {exc}")


def choose_payment_method():
    print("\nPayment method")
    print("1. Card")
    print("2. UPI")
    choice = input("Select [1/2 or Card/UPI]: ").strip().lower()
    simulate_failure = input("Simulate payment failure? [y/N]: ").strip().lower() == "y"

    if choice in {"1", "card"}:
        return CardPayment(simulate_failure=simulate_failure)
    if choice in {"2", "upi"}:
        return UPIPayment(simulate_failure=simulate_failure)

    raise ValidationError("Invalid payment method. Enter 1/Card or 2/UPI.")


def rent_vehicle(service):
    print_header("RENT VEHICLE")
    try:
        customer_id = input("Customer ID: ").strip()
        vehicle_id = input("Vehicle ID: ").strip()
        days = int(input("Rental days: ").strip())
        payment = choose_payment_method()

        rental = service.rent_vehicle(customer_id, vehicle_id, days, payment)
        print("\nRental confirmed successfully.")
        print(f"Rental ID           : {rental.rental_id}")
        print(f"Base rental amount  : Rs. {rental.base_amount:,.2f}")
        print(f"Expected return     : {rental.expected_return_date}")
        print(f"Payment transaction : {rental.payment_result.transaction_id}")
    except (RentalError, ValueError) as exc:
        print(f"Rental failed: {exc}")


def return_vehicle(service):
    print_header("RETURN VEHICLE")
    try:
        rental_id = input("Rental ID: ").strip()
        rental = service.get_rental(rental_id)
        print(f"Expected return date: {rental.expected_return_date}")
        return_date_text = input("Actual return date [YYYY-MM-DD, Enter=today]: ").strip()
        return_date = date.fromisoformat(return_date_text) if return_date_text else date.today()
        invoice = service.return_vehicle(rental_id, return_date)
        invoice.display()
        print("Vehicle returned successfully and is available again.")
    except (RentalError, ValueError) as exc:
        print(f"Return failed: {exc}")


def customer_history(service):
    print_header("CUSTOMER RENTAL HISTORY")
    try:
        customer = service.get_customer(input("Customer ID: ").strip())
        print(f"Customer: {customer.name}")
        if not customer.rental_history:
            print("No rental history available.")
            return
        for rental in customer.rental_history:
            print(rental)
    except RentalError as exc:
        print(f"Could not load history: {exc}")


def show_rentals(service):
    print_header("RENTAL RECORDS")
    if not service.rentals:
        print("No rental records found.")
        return
    for rental in service.rentals:
        print(rental)


def run_mandatory_demo():
    print_header("MANDATORY ASSIGNMENT DEMO")
    service = create_service()
    seed_demo_records(service)
    print("1. One car, one bike and one van are available for the demo.")
    list_vehicles(service, available_only=True)

    # Keep the scenario repeatable: the demo vehicle is expected to be available.
    demo_car = service.get_vehicle("V101")
    demo_customer_a = service.get_customer("DEMO001")
    demo_customer_b = service.get_customer("DEMO002")
    if not demo_car.is_available():
        print("Demo car is currently rented. Complete its active rental first.")
        return

    print("\n2. Customer A rents V101 for 3 days.")
    rental = service.rent_vehicle("DEMO001", "V101", 3, CardPayment())
    print(f"Base rental amount: Rs. {rental.base_amount:,.2f}")

    print("\n3. Attempt Customer B renting the same car.")
    try:
        service.rent_vehicle("DEMO002", "V101", 3, UPIPayment())
    except RentalError as exc:
        print(f"Expected Vehicle unavailable message: {exc}")

    print("\n4. Payment completed successfully before rental confirmation.")
    print(f"Transaction: {rental.payment_result.transaction_id}")

    late_return_date = rental.expected_return_date + timedelta(days=1)
    print(f"\n5. Return car one day late on {late_return_date}.")
    invoice = service.return_vehicle(rental.rental_id, late_return_date)
    invoice.display()

    print("\n6. Vehicle availability after return:")
    print(f"V101 available = {service.get_vehicle('V101').is_available()}")

    print("\n7. Customer A rental history:")
    for history_item in demo_customer_a.rental_history:
        print(history_item)

    print("\nMandatory scenario completed successfully.")


def main():
    service = create_service()
    while True:
        print_header("VEHICLE RENTAL MANAGEMENT SYSTEM")
        print("1. Display available vehicles")
        print("2. Search vehicles")
        print("3. Register customer")
        print("4. Add vehicle")
        print("5. Rent vehicle")
        print("6. Return vehicle / invoice")
        print("7. Customer rental history")
        print("8. Show rental records")
        print("9. Run mandatory assignment demo")
        print("0. Exit")

        choice = input("\nSelect an option: ").strip()
        if choice == "1":
            list_vehicles(service, available_only=True)
        elif choice == "2":
            search_vehicles(service)
        elif choice == "3":
            register_customer(service)
        elif choice == "4":
            add_vehicle(service)
        elif choice == "5":
            rent_vehicle(service)
        elif choice == "6":
            return_vehicle(service)
        elif choice == "7":
            customer_history(service)
        elif choice == "8":
            show_rentals(service)
        elif choice == "9":
            run_mandatory_demo()
            service = create_service()
        elif choice == "0":
            print("\nThank you for using the Vehicle Rental Management System.")
            break
        else:
            print("Invalid option. Please select a menu number from 0 to 9.")


if __name__ == "__main__":
    main()
