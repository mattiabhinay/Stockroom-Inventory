import contextlib
import io
import os
import tempfile
import unittest

from stockroom import cli


class CliTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(["--db", self.path, *argv])
        return code, out.getvalue(), err.getvalue()

    def test_add_and_list(self):
        code, out, _ = self.run_cli("add", "A1", "Widget", "--quantity", "5", "--price", "2.5")
        self.assertEqual(code, 0)
        self.assertIn("Added A1", out)
        code, out, _ = self.run_cli("list")
        self.assertIn("Widget", out)

    def test_remove_too_much_returns_error_code(self):
        self.run_cli("add", "A1", "Widget", "--quantity", "1")
        code, _, err = self.run_cli("remove", "A1", "5")
        self.assertEqual(code, 1)
        self.assertIn("error:", err)

    def test_unknown_sku_reports_error(self):
        code, _, err = self.run_cli("receive", "ZZZ", "1")
        self.assertEqual(code, 1)
        self.assertIn("ZZZ", err)

    def test_low_stock_command(self):
        self.run_cli("add", "A1", "Widget", "--quantity", "2")
        self.run_cli("add", "A2", "Gadget", "--quantity", "50")
        _, out, _ = self.run_cli("low-stock")
        self.assertIn("Widget", out)
        self.assertNotIn("Gadget", out)


if __name__ == "__main__":
    unittest.main()
