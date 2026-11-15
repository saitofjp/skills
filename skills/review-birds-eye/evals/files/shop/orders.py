def insert_order(conn, data):
    cur = conn.execute(
        "INSERT INTO orders (product_id, qty) VALUES (?, ?)",
        (data["product_id"], data["qty"]),
    )
    return cur.lastrowid
