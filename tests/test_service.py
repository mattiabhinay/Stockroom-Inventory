import unittest

from stockroom import db
from stockroom.errors import (
    DuplicateSku,
    InsufficientStock,
    ItemNotFound,
    ValidationError,
)
from stockroom.service import InventoryService


class ServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = db.connect(":memory:")
        self.service = InventoryService(self.conn)

    def tearDown(self):
        self.conn.close()


class AddItemTests(ServiceTestCase):
    def test_add_item_normalises_sku(self):
        item = self.service.add_item(" ab-1 ", "Widget", quantity=3, unit_price=2.5)
        self.assertEqual(item.sku, "AB-1")
        self.assertEqual(item.quantity, 3)

    def test_add_item_records_initial_movement(self):
        self.service.add_item("A1", "Widget", quantity=4)
        history = self.service.history("A1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].delta, 4)

    def test_duplicate_sku_rejected(self):
        self.service.add_item("A1", "Widget")
        with self.assertRaises(DuplicateSku):
            self.service.add_item("a1", "Other widget")

    def test_negative_quantity_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_item("A1", "Widget", quantity=-1)

    def test_empty_name_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add_item("A1", "   ")


class StockChangeTests(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.service.add_item("A1", "Widget", quantity=10, unit_price=1.0)

    def test_receive_increases_quantity(self):
        item = self.service.receive_stock("A1", 5)
        self.assertEqual(item.quantity, 15)

    def test_remove_decreases_quantity(self):
        item = self.service.remove_stock("A1", 4)
        self.assertEqual(item.quantity, 6)

    def test_remove_more_than_available_fails(self):
        with self.assertRaises(InsufficientStock):
            self.service.remove_stock("A1", 11)
        self.assertEqual(self.service.get_item("A1").quantity, 10)

    def test_zero_amount_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.receive_stock("A1", 0)

    def test_adjust_records_delta(self):
        self.service.adjust_stock("A1", 7, reason="stocktake")
        last = self.service.history("A1")[-1]
        self.assertEqual(last.delta, -3)
        self.assertEqual(last.reason, "stocktake")

    def test_adjust_to_same_quantity_records_nothing(self):
        self.service.adjust_stock("A1", 10)
        self.assertEqual(len(self.service.history("A1")), 1)

    def test_unknown_sku(self):
        with self.assertRaises(ItemNotFound):
            self.service.receive_stock("NOPE", 1)


class QueryTests(ServiceTestCase):
    def setUp(self):
        super().setUp()
        self.service.add_item("A1", "Blue pen", quantity=50, category="stationery")
        self.service.add_item("A2", "Red pen", quantity=3, category="stationery")
        self.service.add_item("B1", "Stapler", quantity=5, category="office")

    def test_list_by_category(self):
        skus = [i.sku for i in self.service.list_items("stationery")]
        self.assertEqual(skus, ["A1", "A2"])

    def test_search_matches_name(self):
        self.assertEqual([i.sku for i in self.service.search("pen")], ["A1", "A2"])

    def test_search_rejects_blank(self):
        with self.assertRaises(ValidationError):
            self.service.search("  ")

    def test_low_stock_includes_threshold_boundary(self):
        skus = [i.sku for i in self.service.low_stock()]
        self.assertEqual(skus, ["A2", "B1"])


if __name__ == "__main__":
    unittest.main()
