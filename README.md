# CodeAlpha — Task 1: Data Redundancy Removal System

> **CodeAlpha Cloud Computing Internship**

A cloud-ready Python system that validates incoming records, detects duplicates at multiple levels, and appends only unique, verified entries to the database — preventing data redundancy without any paid cloud service or external library.

---

## 📌 Features

| Feature | Details |
|---|---|
| **Input Validation** | Name, email, and phone are validated before any DB check |
| **Exact Duplicate Detection** | Normalised comparison of all three fields |
| **Email Duplicate Detection** | Case-insensitive; catches `ALICE@` vs `alice@` |
| **Phone Duplicate Detection** | Strips non-digits; works with `+91-98765 43210` |
| **Fuzzy Name Matching** | `SequenceMatcher` catches near-identical names (≥ 85 % similarity) |
| **SQLite Cloud-DB Simulation** | Drop-in replacement for AWS RDS / Azure SQL / GCP Spanner |
| **Unit Tests** | Full `pytest` suite covering all modules |

---

## 🗂 Project Structure

```
CodeAlpha_DataRedundancyRemoval/
│
├── src/
│   ├── app.py                  # Entry point (demo runner)
│   ├── database.py             # Cloud DB layer (SQLite-backed)
│   ├── redundancy_checker.py   # Duplicate detection engine
│   └── data_validator.py       # Input validation
│
├── tests/
│   └── test_system.py          # pytest unit tests
│
├── data/                       # SQLite DB file created here at runtime
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run (VS Code)

### 1. Clone / open in VS Code
```bash
git clone https://github.com/<your-username>/CodeAlpha_DataRedundancyRemoval.git
cd CodeAlpha_DataRedundancyRemoval
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the demo
```bash
cd src
python app.py
```

**Expected output:**
```
============================================================
   CodeAlpha — Data Redundancy Removal System
============================================================

[INFO] Processing incoming records...

  #    Name                 Email                          Status
  --------------------------------------------------------------------------------
  1    Alice Johnson        alice@example.com              ✅ INSERTED
  2    Bob Smith            bob@example.com                ✅ INSERTED
  3    Alice Johnson        alice@example.com              ⚠️  DUPLICATE — exact duplicate of record id=1
  4    alice johnson        ALICE@EXAMPLE.COM              ⚠️  DUPLICATE — email 'ALICE@EXAMPLE.COM' already exists
  5    Carol Davis          carol@example.com              ✅ INSERTED
  6    Bob S.               bob@example.com                ⚠️  DUPLICATE — email 'bob@example.com' already exists
  7                         noname@example.com             ❌ INVALID  — name is empty
  8    Dave Lee             not-an-email                   ❌ INVALID  — invalid email format
  9    Eve Turner           eve@example.com                ✅ INSERTED
  10   Eve Turner           eve2@example.com               ⚠️  DUPLICATE — phone '9333344444' already exists

[DB] Database (4 records):
  ID     Name                 Email                          Phone
  ----------------------------------------------------------------------
  1      Alice Johnson        alice@example.com              9876543210
  2      Bob Smith            bob@example.com                9123456789
  3      Carol Davis          carol@example.com              9000011111
  4      Eve Turner           eve@example.com                9333344444

[SUMMARY]
  Total received : 10
  Inserted       : 4
  Duplicates     : 4
  Invalid        : 2
```

### 5. Run the tests
```bash
cd ..
python -m pytest tests/ -v
```

---

## 🏗 Architecture

```
Incoming Record
      │
      ▼
┌─────────────────────┐
│   DataValidator     │  ← checks name / email / phone format
└────────┬────────────┘
         │ valid
         ▼
┌─────────────────────┐
│  RedundancyChecker  │  ← exact / email / phone / fuzzy-name
└────────┬────────────┘
         │ unique
         ▼
┌─────────────────────┐
│   CloudDatabase     │  ← SQLite (swap to RDS/Spanner for prod)
└─────────────────────┘
```

---

## ☁️ Cloud Deployment Notes

To deploy on a real cloud database:

- **AWS**: Replace `sqlite3` connection in `database.py` with `psycopg2` pointed at an **RDS PostgreSQL** instance.
- **Azure**: Use `pyodbc` with an **Azure SQL Database** connection string.
- **GCP**: Use `google-cloud-spanner` client for **Cloud Spanner**.

No other code changes are needed — the `CloudDatabase` class is the only layer that touches the DB.

---

## 👨‍💻 Author

**[Your Name]**  
CodeAlpha Cloud Computing Intern  
[LinkedIn Profile] | [GitHub Profile]

---

## 📄 License

This project is submitted as part of the **CodeAlpha Internship Programme**.
