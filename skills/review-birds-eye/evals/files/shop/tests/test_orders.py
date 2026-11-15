import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import api  # noqa: E402
import db  # noqa: E402
from validation import InvalidOrder  # noqa: E402


@pytest.fixture
def conn():
    c = db.connect(":memory:")
    db.init(c)
    c.execute("INSERT INTO products (id, name, price) VALUES (1, 'pen', 120)")
    return c


def test_create_order(conn):
    assert api.create_order(conn, {"product_id": 1, "qty": 2}) == 1


def test_rejects_zero_qty(conn):
    with pytest.raises(InvalidOrder):
        api.create_order(conn, {"product_id": 1, "qty": 0})
