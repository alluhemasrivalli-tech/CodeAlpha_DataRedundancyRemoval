"""
test_system.py — Unit tests for all three modules.
Run:  python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from data_validator import DataValidator
from redundancy_checker import RedundancyChecker
from database import CloudDatabase

# ──────────────────────────────────────────────────────────────────────
# DataValidator tests
# ──────────────────────────────────────────────────────────────────────

class TestDataValidator:
    v = DataValidator()

    def test_valid_record(self):
        ok, msg = self.v.validate("Alice Smith", "alice@example.com", "9876543210")
        assert ok and msg == ""

    def test_empty_name(self):
        ok, msg = self.v.validate("", "alice@example.com", "9876543210")
        assert not ok and "empty" in msg

    def test_bad_email(self):
        ok, msg = self.v.validate("Alice", "not-an-email", "9876543210")
        assert not ok and "email" in msg

    def test_short_phone(self):
        ok, msg = self.v.validate("Alice", "alice@example.com", "123")
        assert not ok and "short" in msg

    def test_name_with_hyphen(self):
        ok, _ = self.v.validate("Mary-Jane Watson", "mj@example.com", "9000000001")
        assert ok

    def test_international_email(self):
        ok, _ = self.v.validate("Carlos", "carlos@empresa.com.br", "5511999990000")
        assert ok


# ──────────────────────────────────────────────────────────────────────
# RedundancyChecker tests
# ──────────────────────────────────────────────────────────────────────

EXISTING = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "phone": "9876543210"},
    {"id": 2, "name": "Bob Smith",     "email": "bob@example.com",   "phone": "9123456789"},
]

class TestRedundancyChecker:
    c = RedundancyChecker()

    def test_unique_record(self):
        new = {"name": "Carol Davis", "email": "carol@example.com", "phone": "9000011111"}
        is_dup, _ = self.c.is_duplicate(new, EXISTING)
        assert not is_dup

    def test_exact_duplicate(self):
        new = {"name": "Alice Johnson", "email": "alice@example.com", "phone": "9876543210"}
        is_dup, reason = self.c.is_duplicate(new, EXISTING)
        assert is_dup and "exact" in reason

    def test_email_duplicate_case_insensitive(self):
        new = {"name": "Alice J.", "email": "ALICE@EXAMPLE.COM", "phone": "0000000000"}
        is_dup, reason = self.c.is_duplicate(new, EXISTING)
        assert is_dup and "email" in reason

    def test_phone_duplicate(self):
        new = {"name": "Eve Turner", "email": "eve@example.com", "phone": "9876543210"}
        is_dup, reason = self.c.is_duplicate(new, EXISTING)
        assert is_dup and "phone" in reason

    def test_no_duplicate_similar_name_different_contact(self):
        new = {"name": "Alice Jackson", "email": "alicejackson@example.com", "phone": "9999999999"}
        is_dup, _ = self.c.is_duplicate(new, EXISTING)
        assert not is_dup


# ──────────────────────────────────────────────────────────────────────
# CloudDatabase tests
# ──────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_db(tmp_path):
    db = CloudDatabase(str(tmp_path / "test.sqlite"))
    yield db
    db.close()

class TestCloudDatabase:
    def test_insert_and_retrieve(self, tmp_db):
        tmp_db.insert("Alice", "alice@test.com", "9000000001")
        records = tmp_db.get_all_records()
        assert len(records) == 1
        assert records[0]["email"] == "alice@test.com"

    def test_count(self, tmp_db):
        tmp_db.insert("Alice", "alice@test.com", "9000000001")
        tmp_db.insert("Bob",   "bob@test.com",   "9000000002")
        assert tmp_db.count() == 2

    def test_delete(self, tmp_db):
        tmp_db.insert("Alice", "alice@test.com", "9000000001")
        rid = tmp_db.get_all_records()[0]["id"]
        assert tmp_db.delete_by_id(rid)
        assert tmp_db.count() == 0

    def test_clear(self, tmp_db):
        tmp_db.insert("Alice", "alice@test.com", "9000000001")
        tmp_db.clear()
        assert tmp_db.count() == 0

    def test_email_unique_constraint(self, tmp_db):
        tmp_db.insert("Alice", "alice@test.com", "9000000001")
        with pytest.raises(Exception):
            tmp_db.insert("Alice2", "alice@test.com", "9000000002")
