class StockroomError(Exception):
    """Base class for all errors raised by this package."""


class ValidationError(StockroomError):
    pass


class ItemNotFound(StockroomError):
    pass


class DuplicateSku(StockroomError):
    pass


class InsufficientStock(StockroomError):
    pass
