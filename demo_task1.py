"""
╔══════════════════════════════════════════════════════╗
║   CodeAlpha Internship — Task 1                      ║
║   Data Redundancy Removal System                     ║
║   Demo Output Script                                 ║
╚══════════════════════════════════════════════════════╝

HOW TO RUN:
    python demo_task1.py

No pip install needed — uses only Python stdlib.
"""

import sqlite3, re, unicodedata, os, time
from difflib import SequenceMatcher

# ── Colours ───────────────────────────────────────────────────────────────────
G  = "\033[92m"   # green
R  = "\033[91m"   # red
Y  = "\033[93m"   # yellow
B  = "\033[94m"   # blue
C  = "\033[96m"   # cyan
W  = "\033[97m"   # white bold
DIM= "\033[2m"
RST= "\033[0m"

def slow_print(text, delay=0.012):
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def banner():
    print()
    print(f"{C}{'═'*62}{RST}")
    print(f"{W}   CodeAlpha Internship  ·  Task 1{RST}")
    print(f"{C}   Data Redundancy Removal System{RST}")
    print(f"{C}{'═'*62}{RST}")
    print()

# ── Validator ─────────────────────────────────────────────────────────────────
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

def validate(name, email, phone):
    if not name.strip() or len(name.strip()) < 2:
        return False, "name is empty or too short"
    if re.search(r"[^a-zA-Z\s\-\'\u00C0-\u024F]", name.strip()):
        return False, "name contains invalid characters"
    if not EMAIL_RE.match(email.strip()):
        return False, f"invalid email format"
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return False, "phone too short"
    return True, ""

# ── Duplicate checker ─────────────────────────────────────────────────────────
def normalise(t):
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t).strip().lower()

def clean_phone(p): return re.sub(r"\D", "", p)

def is_duplicate(new, existing):
    ne = normalise(new["email"]); np = clean_phone(new["phone"]); nn = normalise(new["name"])
    for ex in existing:
        ee = normalise(ex["email"]); ep = clean_phone(ex["phone"]); en = normalise(ex["name"])
        if ne == ee and np == ep and nn == en:
            return True, f"exact duplicate of id={ex['id']}"
        if ne == ee:
            return True, f"email '{new['email']}' already exists (id={ex['id']})"
        if np and ep and np == ep:
            return True, f"phone '{new['phone']}' already exists (id={ex['id']})"
    return False, ""

# ── In-memory DB ──────────────────────────────────────────────────────────────
conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("""CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, phone TEXT NOT NULL
)""")
conn.commit()

def insert(name, email, phone):
    conn.execute("INSERT INTO users (name,email,phone) VALUES (?,?,?)",
                 (name.strip(), email.strip().lower(), phone.strip()))
    conn.commit()

def get_all():
    return [dict(r) for r in conn.execute("SELECT * FROM users ORDER BY id").fetchall()]

# ── Sample incoming data ───────────────────────────────────────────────────────
incoming = [
    {"name": "Alice Johnson",  "email": "alice@example.com",  "phone": "9876543210"},
    {"name": "Bob Smith",      "email": "bob@example.com",    "phone": "9123456789"},
    {"name": "Alice Johnson",  "email": "alice@example.com",  "phone": "9876543210"},  # exact dup
    {"name": "alice johnson",  "email": "ALICE@EXAMPLE.COM",  "phone": "9876543210"},  # case dup
    {"name": "Carol Davis",    "email": "carol@example.com",  "phone": "9000011111"},
    {"name": "Bob S.",         "email": "bob@example.com",    "phone": "9999999999"},  # email dup
    {"name": "",               "email": "noname@example.com", "phone": "9111122222"},  # invalid
    {"name": "Dave Lee",       "email": "not-an-email",       "phone": "9222233333"},  # invalid
    {"name": "Eve Turner",     "email": "eve@example.com",    "phone": "9333344444"},
    {"name": "Eve Turner",     "email": "eve2@example.com",   "phone": "9333344444"},  # phone dup
]

# ── Run demo ───────────────────────────────────────────────────────────────────
banner()
slow_print(f"{DIM}Initialising cloud database...{RST}", 0.02)
time.sleep(0.4)
slow_print(f"{DIM}Loading validation engine...{RST}", 0.02)
time.sleep(0.4)
slow_print(f"{DIM}Loading redundancy checker...{RST}", 0.02)
time.sleep(0.4)
print()
print(f"{W}[INFO]{RST} Processing {len(incoming)} incoming records...\n")
time.sleep(0.3)

# Header
print(f"  {DIM}{'#':<4} {'Name':<20} {'Email':<30} Status{RST}")
print(f"  {'─'*78}")

stats = {"inserted": 0, "duplicate": 0, "invalid": 0}

for i, rec in enumerate(incoming, 1):
    time.sleep(0.35)
    name, email, phone = rec["name"], rec["email"], rec["phone"]

    ok, reason = validate(name, email, phone)
    if not ok:
        stats["invalid"] += 1
        print(f"  {i:<4} {name:<20} {email:<30} {R}❌ INVALID  — {reason}{RST}")
        continue

    dup, dup_reason = is_duplicate(rec, get_all())
    if dup:
        stats["duplicate"] += 1
        print(f"  {i:<4} {name:<20} {email:<30} {Y}⚠  DUPLICATE — {dup_reason}{RST}")
        continue

    insert(name, email, phone)
    stats["inserted"] += 1
    print(f"  {i:<4} {name:<20} {email:<30} {G}✅ INSERTED{RST}")

# Database snapshot
print()
print(f"{C}{'─'*62}{RST}")
records = get_all()
print(f"{W}[DATABASE]{RST} Final state — {G}{len(records)} unique records{RST} stored:\n")
print(f"  {DIM}{'ID':<6} {'Name':<20} {'Email':<30} {'Phone'}{RST}")
print(f"  {'─'*70}")
for r in records:
    time.sleep(0.15)
    print(f"  {r['id']:<6} {r['name']:<20} {r['email']:<30} {r['phone']}")

# Summary
print()
print(f"{C}{'═'*62}{RST}")
print(f"{W}[SUMMARY]{RST}")
print(f"  Total received  : {W}{len(incoming)}{RST}")
print(f"  {G}✅ Inserted     : {stats['inserted']}{RST}")
print(f"  {Y}⚠  Duplicates   : {stats['duplicate']}{RST}")
print(f"  {R}❌ Invalid       : {stats['invalid']}{RST}")
print()
print(f"{G}  ✔  System successfully prevented {stats['duplicate'] + stats['invalid']} bad records!{RST}")
print(f"{C}{'═'*62}{RST}")
print()
