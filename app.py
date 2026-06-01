"""
CodeAlpha Internship — Task 1: Data Redundancy Removal System
Entry point: runs the interactive CLI demo.
"""

from database import CloudDatabase
from redundancy_checker import RedundancyChecker
from data_validator import DataValidator


def print_banner():
    print("=" * 60)
    print("   CodeAlpha — Data Redundancy Removal System")
    print("=" * 60)


def print_db(db: CloudDatabase):
    records = db.get_all_records()
    if not records:
        print("\n[DB] Database is empty.")
        return
    print(f"\n[DB] Database ({len(records)} records):")
    print(f"  {'ID':<6} {'Name':<20} {'Email':<30} {'Phone':<15}")
    print("  " + "-" * 70)
    for r in records:
        print(f"  {r['id']:<6} {r['name']:<20} {r['email']:<30} {r['phone']:<15}")


def run_demo():
    print_banner()

    db = CloudDatabase()
    checker = RedundancyChecker()
    validator = DataValidator()

    sample_data = [
        {"name": "Alice Johnson",  "email": "alice@example.com",  "phone": "9876543210"},
        {"name": "Bob Smith",      "email": "bob@example.com",    "phone": "9123456789"},
        {"name": "Alice Johnson",  "email": "alice@example.com",  "phone": "9876543210"},  # exact duplicate
        {"name": "alice johnson",  "email": "ALICE@EXAMPLE.COM",  "phone": "9876543210"},  # case duplicate
        {"name": "Carol Davis",    "email": "carol@example.com",  "phone": "9000011111"},
        {"name": "Bob S.",         "email": "bob@example.com",    "phone": "9999999999"},  # email duplicate
        {"name": "",               "email": "noname@example.com", "phone": "9111122222"},  # invalid: empty name
        {"name": "Dave Lee",       "email": "not-an-email",       "phone": "9222233333"},  # invalid: bad email
        {"name": "Eve Turner",     "email": "eve@example.com",    "phone": "9333344444"},
        {"name": "Eve Turner",     "email": "eve2@example.com",   "phone": "9333344444"},  # phone duplicate
    ]

    print("\n[INFO] Processing incoming records...\n")
    print(f"  {'#':<4} {'Name':<20} {'Email':<30} {'Status'}")
    print("  " + "-" * 80)

    stats = {"inserted": 0, "duplicate": 0, "invalid": 0}

    for i, record in enumerate(sample_data, 1):
        name   = record.get("name", "")
        email  = record.get("email", "")
        phone  = record.get("phone", "")

        # Step 1: Validate
        is_valid, reason = validator.validate(name, email, phone)
        if not is_valid:
            stats["invalid"] += 1
            print(f"  {i:<4} {name:<20} {email:<30} ❌ INVALID  — {reason}")
            continue

        # Step 2: Check redundancy
        is_dup, dup_reason = checker.is_duplicate(record, db.get_all_records())
        if is_dup:
            stats["duplicate"] += 1
            print(f"  {i:<4} {name:<20} {email:<30} ⚠️  DUPLICATE — {dup_reason}")
            continue

        # Step 3: Insert unique + valid record
        db.insert(name, email, phone)
        stats["inserted"] += 1
        print(f"  {i:<4} {name:<20} {email:<30} ✅ INSERTED")

    print_db(db)

    print("\n[SUMMARY]")
    print(f"  Total received : {len(sample_data)}")
    print(f"  Inserted       : {stats['inserted']}")
    print(f"  Duplicates     : {stats['duplicate']}")
    print(f"  Invalid        : {stats['invalid']}")
    print("\n[DONE] Redundancy removal complete.\n")


if __name__ == "__main__":
    run_demo()
