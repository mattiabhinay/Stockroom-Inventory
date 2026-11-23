from . import config
from .errors import DuplicateSku, InsufficientStock, ItemNotFound, ValidationError
from .repository import ItemRepository, MovementRepository


class InventoryService:
    def __init__(self, conn):
        self.conn = conn
        self.items = ItemRepository(conn)
        self.movements = MovementRepository(conn)

    # -- lookups ---------------------------------------------------------

    def get_item(self, sku):
        item = self.items.get_by_sku(sku)
        if item is None:
            raise ItemNotFound(f"No item with SKU '{sku}'")
        return item

    def list_items(self, category=None):
        return self.items.list_all(category)

    def search(self, term):
        if not term or not term.strip():
            raise ValidationError("Search term must not be empty")
        return self.items.search(term.strip())

    def low_stock(self):
        return [
            i for i in self.items.list_all()
            if i.quantity <= config.LOW_STOCK_THRESHOLD
        ]

    def history(self, sku):
        item = self.get_item(sku)
        return self.movements.for_item(item.id)

    # -- changes ---------------------------------------------------------

    def add_item(self, sku, name, quantity=0, unit_price=0.0, category="general"):
        if not sku or not sku.strip():
            raise ValidationError("SKU must not be empty")
        if not name or not name.strip():
            raise ValidationError("Name must not be empty")
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        if unit_price < 0:
            raise ValidationError("Unit price cannot be negative")
        sku = sku.strip().upper()
        if self.items.get_by_sku(sku) is not None:
            raise DuplicateSku(f"SKU '{sku}' already exists")
        with self.conn:
            item = self.items.add(sku, name.strip(), quantity, unit_price, category)
            if quantity > 0:
                self.movements.record(item.id, quantity, "initial stock")
        return item

    def receive_stock(self, sku, amount, reason="restock"):
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        item = self.get_item(sku.strip().upper())
        with self.conn:
            self.items.set_quantity(item.id, item.quantity + amount)
            self.movements.record(item.id, amount, reason)
        return self.items.get(item.id)

    def remove_stock(self, sku, amount, reason="sale"):
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        item = self.get_item(sku.strip().upper())
        if item.quantity < amount:
            raise InsufficientStock(
                f"Only {item.quantity} of '{item.sku}' in stock, cannot remove {amount}"
            )
        with self.conn:
            self.items.set_quantity(item.id, item.quantity - amount)
            self.movements.record(item.id, -amount, reason)
        return self.items.get(item.id)

    def adjust_stock(self, sku, new_quantity, reason="adjustment"):
        if new_quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        item = self.get_item(sku.strip().upper())
        delta = new_quantity - item.quantity
        if delta == 0:
            return item
        with self.conn:
            self.items.set_quantity(item.id, new_quantity)
            self.movements.record(item.id, delta, reason)
        return self.items.get(item.id)
