from orders import insert_order
from validation import validate_order


def create_order(conn, data):
    validate_order(conn, data)
    order_id = insert_order(conn, data)
    conn.commit()
    return order_id


def get_product(conn, product_id):
    row = conn.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,)).fetchone()
    return dict(row) if row else None


def list_products(conn):
    rows = conn.execute("SELECT id, name, price FROM products ORDER BY id").fetchall()
    return [dict(r) for r in rows]
