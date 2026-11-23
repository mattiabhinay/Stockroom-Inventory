import csv


def inventory_value(items):
    """Total value of everything on the shelves."""
    return sum(i.quantity * i.unit_price for i in items)


def category_summary(items):
    summary = {}
    for i in items:
        entry = summary.setdefault(i.category, {"items": 0, "units": 0, "value": 0.0})
        entry["items"] += 1
        entry["units"] += i.quantity
        entry["value"] += i.quantity * i.unit_price
    return summary


def export_csv(items, fileobj):
    writer = csv.writer(fileobj)
    writer.writerow(["sku", "name", "category", "quantity", "unit_price", "value"])
    for i in items:
        writer.writerow(
            [i.sku, i.name, i.category, i.quantity, i.unit_price, i.quantity * i.unit_price]
        )
