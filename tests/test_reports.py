import io
import unittest

from stockroom import reports
from stockroom.models import Item


def make_items():
    return [
        Item(1, "A1", "Blue pen", 10, 1.50, "stationery"),
        Item(2, "A2", "Red pen", 4, 2.00, "stationery"),
        Item(3, "B1", "Stapler", 2, 7.25, "office"),
    ]


class ReportTests(unittest.TestCase):
    def test_inventory_value(self):
        self.assertAlmostEqual(reports.inventory_value(make_items()), 37.5)

    def test_category_summary(self):
        summary = reports.category_summary(make_items())
        self.assertEqual(summary["stationery"]["units"], 14)
        self.assertEqual(summary["office"]["items"], 1)
        self.assertAlmostEqual(summary["stationery"]["value"], 23.0)

    def test_export_csv_has_header_and_rows(self):
        buf = io.StringIO()
        reports.export_csv(make_items(), buf)
        lines = buf.getvalue().strip().splitlines()
        self.assertEqual(lines[0], "sku,name,category,quantity,unit_price,value")
        self.assertEqual(len(lines), 4)

    def test_export_csv_quotes_commas_in_names(self):
        buf = io.StringIO()
        reports.export_csv([Item(1, "C1", "Pens, assorted", 1, 1.0)], buf)
        self.assertIn('"Pens, assorted"', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
