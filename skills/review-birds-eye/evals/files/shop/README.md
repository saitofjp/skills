# shop

A small order service on SQLite.

Orders come in two ways:

- `api.create_order` — one order from the web.
- `import_orders.import_csv` — the nightly batch, many orders from a partner's CSV.

Both check an order with `validation.validate_order` and write it with `orders.insert_order`.

`db.init` creates the tables on a new database. Existing databases are changed by the scripts in `migrations/`, applied in order.
