from dataclasses import dataclass


@dataclass
class Item:
    id: int
    sku: str
    name: str
    quantity: int
    unit_price: float
    category: str = "general"


@dataclass
class Movement:
    id: int
    item_id: int
    delta: int
    reason: str
    created_at: str
