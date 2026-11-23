import os

DEFAULT_DB_PATH = os.environ.get("STOCKROOM_DB", "stockroom.db")

# Items at or below this quantity show up in the low-stock report.
LOW_STOCK_THRESHOLD = 5
