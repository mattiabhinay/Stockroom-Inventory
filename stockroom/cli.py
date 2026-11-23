import argparse
import sys

from . import config, db, reports
from .errors import StockroomError
from .service import InventoryService


def _print_items(items):
    if not items:
        print("No items found.")
        return
    print(f"{'SKU':<12}{'NAME':<28}{'CATEGORY':<14}{'QTY':>6}{'PRICE':>10}")
    for i in items:
        print(f"{i.sku:<12}{i.name:<28}{i.category:<14}{i.quantity:>6}{i.unit_price:>10.2f}")


def build_parser():
    parser = argparse.ArgumentParser(prog="stockroom", description="Track shop inventory")
    parser.add_argument("--db", default=config.DEFAULT_DB_PATH, help="path to database file")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add a new item")
    p.add_argument("sku")
    p.add_argument("name")
    p.add_argument("--quantity", type=int, default=0)
    p.add_argument("--price", type=float, default=0.0)
    p.add_argument("--category", default="general")

    p = sub.add_parser("receive", help="add stock to an item")
    p.add_argument("sku")
    p.add_argument("amount", type=int)
    p.add_argument("--reason", default="restock")

    p = sub.add_parser("remove", help="remove stock from an item")
    p.add_argument("sku")
    p.add_argument("amount", type=int)
    p.add_argument("--reason", default="sale")

    p = sub.add_parser("adjust", help="set an item's quantity directly")
    p.add_argument("sku")
    p.add_argument("quantity", type=int)
    p.add_argument("--reason", default="adjustment")

    p = sub.add_parser("list", help="list items")
    p.add_argument("--category")

    p = sub.add_parser("search", help="search by name or SKU")
    p.add_argument("term")

    sub.add_parser("low-stock", help="show items running low")
    sub.add_parser("report", help="show inventory value by category")
    sub.add_parser("export", help="write all items to CSV on stdout")
    return parser


def run(args, service):
    cmd = args.command
    if cmd == "add":
        item = service.add_item(args.sku, args.name, args.quantity, args.price, args.category)
        print(f"Added {item.sku} ({item.name}), quantity {item.quantity}")
    elif cmd == "receive":
        item = service.receive_stock(args.sku, args.amount, args.reason)
        print(f"{item.sku} now has {item.quantity} in stock")
    elif cmd == "remove":
        item = service.remove_stock(args.sku, args.amount, args.reason)
        print(f"{item.sku} now has {item.quantity} in stock")
    elif cmd == "adjust":
        item = service.adjust_stock(args.sku, args.quantity, args.reason)
        print(f"{item.sku} now has {item.quantity} in stock")
    elif cmd == "list":
        _print_items(service.list_items(args.category))
    elif cmd == "search":
        _print_items(service.search(args.term))
    elif cmd == "low-stock":
        _print_items(service.low_stock())
    elif cmd == "report":
        items = service.list_items()
        for category, s in sorted(reports.category_summary(items).items()):
            print(f"{category:<14}{s['items']:>4} items{s['units']:>7} units{s['value']:>12.2f}")
        print(f"{'TOTAL':<14}{'':>4}      {'':>7}      {reports.inventory_value(items):>12.2f}")
    elif cmd == "export":
        reports.export_csv(service.list_items(), sys.stdout)


def main(argv=None):
    args = build_parser().parse_args(argv)
    conn = db.connect(args.db)
    try:
        run(args, InventoryService(conn))
    except StockroomError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
