class Invoice:
    """Invoice generated for a completed rental."""

    def __init__(self, rental):
        self.__rental = rental

    def generate(self):
        vehicle = self.__rental.vehicle
        return {
            "rental_id": self.__rental.rental_id,
            "customer_id": self.__rental.customer.customer_id,
            "customer_name": self.__rental.customer.name,
            "vehicle_id": vehicle.vehicle_id,
            "vehicle_type": vehicle.vehicle_type,
            "vehicle_brand": vehicle.brand,
            "vehicle_model": vehicle.model,
            "rental_days": self.__rental.days,
            "base_amount": round(self.__rental.base_amount, 2),
            "late_fee": round(self.__rental.late_fee, 2),
            "final_amount": round(self.__rental.final_amount, 2),
        }

    def display(self):
        data = self.generate()
        print("\n" + "=" * 55)
        print("                 FINAL RENTAL INVOICE")
        print("=" * 55)
        print(f"Rental ID       : {data['rental_id']}")
        print(f"Customer        : {data['customer_name']} ({data['customer_id']})")
        print(f"Vehicle         : {data['vehicle_type']} {data['vehicle_id']}")
        print(f"Model           : {data['vehicle_brand']} {data['vehicle_model']}")
        print(f"Rental Days     : {data['rental_days']}")
        print(f"Base Amount     : Rs. {data['base_amount']:,.2f}")
        print(f"Late Fee        : Rs. {data['late_fee']:,.2f}")
        print(f"Final Amount    : Rs. {data['final_amount']:,.2f}")
        print("=" * 55)

    def __str__(self):
        data = self.generate()
        return (
            f"{data['rental_id']} | {data['customer_name']} | "
            f"{data['vehicle_type']} {data['vehicle_id']} | "
            f"Rs. {data['final_amount']:,.2f} | {self.__rental.status}"
        )
