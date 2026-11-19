import sqlite3
from pathlib import Path

MIGRATIONS = Path(__file__).parent / "migrations"


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init(conn):
    """Create the tables on a new database by applying every migration in order."""
    for script in sorted(MIGRATIONS.glob("*.sql")):
        conn.executescript(script.read_text())
    conn.commit()
