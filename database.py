"""
database.py — Simulated in-memory cloud database.

In a real deployment this would connect to AWS RDS, Azure SQL, or
Google Cloud Spanner. For the internship demo we keep everything in RAM
so there are zero external dependencies.
"""

import sqlite3
import os
from typing import List, Dict


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cloud_db.sqlite")


class CloudDatabase:
    """
    Lightweight SQLite-backed database that mimics a cloud database.
    Switch the connection string to any cloud DB without changing the API.
    """

    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                email     TEXT    NOT NULL UNIQUE,
                phone     TEXT    NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def insert(self, name: str, email: str, phone: str) -> int:
        """Insert a verified-unique record and return its new ID."""
        cur = self.conn.execute(
            "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)",
            (name.strip(), email.strip().lower(), phone.strip()),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_all_records(self) -> List[Dict]:
        """Return all rows as a list of plain dicts."""
        rows = self.conn.execute(
            "SELECT id, name, email, phone FROM users ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]

    def delete_by_id(self, record_id: int) -> bool:
        """Delete a record by primary key. Returns True if a row was removed."""
        cur = self.conn.execute("DELETE FROM users WHERE id = ?", (record_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def clear(self):
        """Wipe all records (useful for tests)."""
        self.conn.execute("DELETE FROM users")
        self.conn.commit()

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def close(self):
        self.conn.close()
