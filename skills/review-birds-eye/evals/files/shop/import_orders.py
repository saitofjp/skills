import csv

from orders import insert_order
from validation import InvalidOrder, validate_order


def import_csv(conn, path):
    """Nightly batch. Returns (imported, rejected)."""
    imported, rejected = 0, []
    with open(path, newline="", encoding="utf-8") as f:
        for n, row in enumerate(csv.DictReader(f), 2):
            data = {"product_id": int(row["product_id"]), "qty": int(row["qty"])}
            try:
                validate_order(conn, data)
            except InvalidOrder as exc:
                rejected.append((n, str(exc)))
                continue
            insert_order(conn, data)
            imported += 1
    conn.commit()
    return imported, rejected
