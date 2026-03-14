class ServiceError(Exception):
    """Raised when a service-level operation fails."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass
