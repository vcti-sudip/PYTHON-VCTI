from datetime import date
from pathlib import Path

import streamlit as st

from main import create_service
from schemas.customers import Customer
from schemas.exceptions import RentalError
from schemas.payment import CardPayment, UPIPayment
from schemas.vehicles import Bike, Car, Van


st.set_page_config(page_title="Rent Your Ride", page_icon="R", layout="wide")


@st.cache_resource
def get_service():
    return create_service()


def money(amount):
    return f"Rs. {amount:,.2f}"


def vehicle_label(vehicle):
    return f"{vehicle.vehicle_id} - {vehicle.brand} {vehicle.model} ({vehicle.vehicle_type})"


def show_vehicle_table(vehicles):
    if not vehicles:
        st.info("No vehicles match your search.")
        return
    rows = [
        {
            "ID": vehicle.vehicle_id,
            "Type": vehicle.vehicle_type,
            "Vehicle": f"{vehicle.brand} {vehicle.model}",
            "Registration": vehicle.registration_number,
            "Daily rate": money(vehicle.daily_rate),
            "Status": "Available" if vehicle.is_available() else "Rented",
        }
        for vehicle in vehicles
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def browse_page(service):
    st.title("Find your next ride")
    st.caption("Browse available cars, bikes, and vans, then book in a few clicks.")
    search_id = st.text_input("Search by vehicle ID", placeholder="For example, KA001")
    left, middle, right = st.columns(3)
    with left:
        vehicle_type = st.selectbox("Vehicle type", ["All", "Car", "Bike", "Van"])
    with middle:
        minimum = st.number_input("Minimum daily rate", min_value=0.0, value=0.0, step=100.0)
    with right:
        maximum = st.number_input("Maximum daily rate", min_value=0.0, value=10000.0, step=100.0)

    selected_type = None if vehicle_type == "All" else vehicle_type
    vehicles = service.search(
        vehicle_id=search_id.strip() or None,
        vehicle_type=selected_type,
        min_price=minimum,
        max_price=maximum,
    )
    available = [vehicle for vehicle in vehicles if vehicle.is_available()]
    st.subheader(f"{len(available)} rides available")
    show_vehicle_table(available)


def booking_page(service):
    st.title("Book a ride")
    available = [vehicle for vehicle in service.vehicles if vehicle.is_available()]
    if not available:
        st.warning("There are no available vehicles right now.")
        return

    with st.form("booking_form"):
        vehicle = st.selectbox("Choose a vehicle", available, format_func=vehicle_label)
        customer_options = list(service.customers)
        customer = st.selectbox(
            "Customer", customer_options, format_func=lambda item: f"{item.name} ({item.customer_id})"
        )
        start_date = st.date_input("Pick-up date", value=date.today(), min_value=date.today())
        days = st.number_input("Rental days", min_value=1, max_value=365, value=1, step=1)
        payment_method = st.radio("Payment method", ["Card", "UPI"], horizontal=True)
        submitted = st.form_submit_button("Confirm booking", type="primary")

    estimate = vehicle.calculate_rental_cost(int(days))
    st.metric("Estimated total", money(estimate))
    if submitted:
        payment = CardPayment() if payment_method == "Card" else UPIPayment()
        try:
            rental = service.rent_vehicle(
                customer.customer_id, vehicle.vehicle_id, int(days), payment, start_date=start_date
            )
            st.success(f"Booking confirmed. Rental ID: {rental.rental_id}")
            st.write(
                f"Return by **{rental.expected_return_date}**. "
                f"Transaction: `{rental.payment_result.transaction_id}`"
            )
        except RentalError as error:
            st.error(str(error))


def return_page(service):
    st.title("Return a vehicle")
    active = [rental for rental in service.rentals if rental.status == "ACTIVE"]
    if not active:
        st.info("There are no active rentals to return.")
        return

    with st.form("return_form"):
        rental = st.selectbox(
            "Active rental",
            active,
            format_func=lambda item: f"{item.rental_id} - {item.vehicle.brand} {item.vehicle.model} for {item.customer.name}",
        )
        st.caption(f"Expected return: {rental.expected_return_date}")
        return_date = st.date_input("Actual return date", value=date.today(), min_value=rental.start_date)
        submitted = st.form_submit_button("Return vehicle", type="primary")

    if submitted:
        try:
            invoice = service.return_vehicle(rental.rental_id, return_date)
            details = invoice.generate()
            st.success(f"Vehicle returned. Invoice {rental.rental_id} is ready.")
            st.json(details)
        except RentalError as error:
            st.error(str(error))


def customers_page(service):
    st.title("Customers and history")
    with st.expander("Register a new customer"):
        with st.form("customer_form"):
            customer_id = st.text_input("Customer ID")
            name = st.text_input("Name")
            email = st.text_input("Email")
            license_number = st.text_input("Driving licence number")
            submitted = st.form_submit_button("Register customer")
        if submitted:
            try:
                service.register_customer(Customer(customer_id, name, email, license_number))
                st.success("Customer registered successfully.")
            except RentalError as error:
                st.error(str(error))

    if not service.customers:
        st.info("No customers registered yet.")
        return
    customer = st.selectbox("View rental history for", service.customers, format_func=lambda item: item.name)
    st.dataframe(
        [
            {
                "Rental ID": rental.rental_id,
                "Vehicle": f"{rental.vehicle.brand} {rental.vehicle.model}",
                "Dates": f"{rental.start_date} to {rental.actual_return_date or rental.expected_return_date}",
                "Amount": money(rental.final_amount),
                "Status": rental.status,
            }
            for rental in customer.rental_history
        ],
        use_container_width=True,
        hide_index=True,
    )


def management_page(service):
    st.title("Rental records")
    st.dataframe(
        [
            {
                "Rental ID": rental.rental_id,
                "Customer": rental.customer.name,
                "Vehicle": vehicle_label(rental.vehicle),
                "Start date": rental.start_date,
                "Status": rental.status,
                "Amount": money(rental.final_amount),
            }
            for rental in service.rentals
        ],
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Add a vehicle"):
        with st.form("vehicle_form"):
            vehicle_type = st.selectbox("Type", ["Car", "Bike", "Van"])
            vehicle_id = st.text_input("Vehicle ID")
            registration = st.text_input("Registration number")
            brand = st.text_input("Brand")
            model = st.text_input("Model")
            daily_rate = st.number_input("Daily rental rate", min_value=0.01, value=1000.0, step=100.0)
            service_charge = st.number_input("Van service charge", min_value=0.0, value=500.0, step=50.0)
            submitted = st.form_submit_button("Add vehicle")
        if submitted:
            try:
                vehicle_class = {"Car": Car, "Bike": Bike, "Van": Van}[vehicle_type]
                if vehicle_type == "Van":
                    vehicle = vehicle_class(vehicle_id, registration, brand, model, daily_rate, service_charge)
                else:
                    vehicle = vehicle_class(vehicle_id, registration, brand, model, daily_rate)
                service.add_vehicle(vehicle)
                st.success("Vehicle added successfully.")
            except RentalError as error:
                st.error(str(error))


def main():
    service = get_service()
    st.sidebar.title("Rent Your Ride")
    st.sidebar.caption("Simple vehicle rental management")
    page = st.sidebar.radio("Navigate", ["Browse rides", "Book a ride", "Return vehicle", "Customers", "Records"])
    if page == "Browse rides":
        browse_page(service)
    elif page == "Book a ride":
        booking_page(service)
    elif page == "Return vehicle":
        return_page(service)
    elif page == "Customers":
        customers_page(service)
    else:
        management_page(service)


if __name__ == "__main__":
    main()