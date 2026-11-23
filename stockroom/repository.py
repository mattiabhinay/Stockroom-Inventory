from datetime import datetime, timezone

from .models import Item, Movement


def _row_to_item(row):
    return Item(
        id=row["id"],
        sku=row["sku"],
        name=row["name"],
        quantity=row["quantity"],
        unit_price=row["unit_price"],
        category=row["category"],
    )


class ItemRepository:
    def __init__(self, conn):
        self.conn = conn

    def add(self, sku, name, quantity, unit_price, category):
        cur = self.conn.execute(
            "INSERT INTO items (sku, name, quantity, unit_price, category) "
            "VALUES (?, ?, ?, ?, ?)",
            (sku, name, quantity, unit_price, category),
        )
        return self.get(cur.lastrowid)

    def get(self, item_id):
        row = self.conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        return _row_to_item(row) if row else None

    def get_by_sku(self, sku):
        row = self.conn.execute(
            "SELECT * FROM items WHERE sku = ?", (sku,)
        ).fetchone()
        return _row_to_item(row) if row else None

    def list_all(self, category=None):
        if category:
            rows = self.conn.execute(
                "SELECT * FROM items WHERE category = ? ORDER BY sku", (category,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM items ORDER BY sku").fetchall()
        return [_row_to_item(r) for r in rows]

    def search(self, term):
        like = f"%{term}%"
        rows = self.conn.execute(
            "SELECT * FROM items WHERE name LIKE ? OR sku LIKE ? ORDER BY sku",
            (like, like),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def set_quantity(self, item_id, quantity):
        self.conn.execute(
            "UPDATE items SET quantity = ? WHERE id = ?", (quantity, item_id)
        )


class MovementRepository:
    def __init__(self, conn):
        self.conn = conn

    def record(self, item_id, delta, reason):
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.conn.execute(
            "INSERT INTO movements (item_id, delta, reason, created_at) "
            "VALUES (?, ?, ?, ?)",
            (item_id, delta, reason, created_at),
        )

    def for_item(self, item_id):
        rows = self.conn.execute(
            "SELECT * FROM movements WHERE item_id = ? ORDER BY id", (item_id,)
        ).fetchall()
        return [
            Movement(
                id=r["id"],
                item_id=r["item_id"],
                delta=r["delta"],
                reason=r["reason"],
                created_at=r["created_at"],
            )
            for r in rows
        ]
