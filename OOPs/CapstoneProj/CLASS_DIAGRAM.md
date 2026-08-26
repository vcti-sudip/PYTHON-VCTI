# Class Diagram

```mermaid
classDiagram
    Vehicle <|-- Car
    Vehicle <|-- Bike
    Vehicle <|-- Van
    PaymentProcessor <|.. CardPayment
    PaymentProcessor <|.. UPIPayment
    Rental *-- Customer
    Rental *-- Vehicle
    Rental *-- PaymentResult
    Rental *-- Invoice
    Customer o-- Rental
    RentalService --> Rental
    RentalService --> PaymentProcessor

    class Vehicle {
        <<abstract>>
        - vehicle_id
        - registration_number
        - brand
        - model
        - daily_rate
        - available
        + calculate_rental_cost(days)
        + display_details()
        + mark_as_rented()
        + mark_as_available()
    }

    class RentalService {
        + rent_vehicle(customer_id, vehicle_id, days, payment_processor)
        + return_vehicle(rental_id, return_date)
        + search(...)
    }
