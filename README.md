# Stockroom

A small inventory tracker for a single shop. It stores items and every stock
movement in a local SQLite file and ships with a command-line interface.

Requires Python 3.10+ and nothing else.

## Usage

```bash
python -m stockroom add PEN-01 "Blue pen" --quantity 40 --price 1.20 --category stationery
python -m stockroom receive PEN-01 20
python -m stockroom remove PEN-01 5 --reason "sale"
python -m stockroom adjust PEN-01 52 --reason "stocktake"
python -m stockroom list --category stationery
python -m stockroom search pen
python -m stockroom low-stock
python -m stockroom report
python -m stockroom export > items.csv
```

The database path defaults to `stockroom.db` in the current directory. Override
it with `--db PATH` or the `STOCKROOM_DB` environment variable.

## Layout

- `stockroom/service.py` - business rules (validation, stock changes)
- `stockroom/repository.py` - SQL access
- `stockroom/reports.py` - valuation, category summary, CSV export
- `stockroom/cli.py` - argparse front end
- `tests/` - unit tests

## Tests

```bash
python -m unittest discover -v
```
