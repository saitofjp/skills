class InvalidOrder(Exception):
    pass


def validate_order(conn, data):
    """The one place an order is checked. Every way in calls this before writing."""
    qty = data.get("qty")
    if not isinstance(qty, int) or qty < 1:
        raise InvalidOrder("qty must be a positive integer")
    row = conn.execute("SELECT id FROM products WHERE id = ?", (data.get("product_id"),)).fetchone()
    if row is None:
        raise InvalidOrder("unknown product")
