class RentalError(Exception):
    """Base exception for the vehicle rental system."""


class ValidationError(RentalError):
    """Raised when input data fails validation."""


class VehicleNotFoundError(RentalError):
    """Raised when a requested vehicle does not exist."""


class VehicleNotAvailableError(RentalError):
    """Raised when a vehicle is unavailable for rental."""


class CustomerNotFoundError(RentalError):
    """Raised when a requested customer does not exist."""


class InvalidRentalPeriodError(RentalError):
    """Raised when rental duration or dates are invalid."""


class PaymentProcessingError(RentalError):
    """Raised when payment does not complete successfully."""


class RentalStateError(RentalError):
    """Raised when an invalid rental-state operation is attempted."""
