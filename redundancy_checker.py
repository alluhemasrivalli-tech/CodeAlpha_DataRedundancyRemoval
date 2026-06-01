"""
redundancy_checker.py — Core duplicate-detection logic.

Classification levels
─────────────────────
1. EXACT DUPLICATE   — identical values across all normalised fields
2. EMAIL DUPLICATE   — same email address (case-insensitive)
3. PHONE DUPLICATE   — same phone number after stripping non-digits
4. FUZZY NAME MATCH  — same email + very similar name (handles typos)

The checker returns (is_duplicate: bool, reason: str) so the caller
knows *why* a record was rejected.
"""

from __future__ import annotations
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, List, Tuple


def _normalise(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip().lower()


def _clean_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def _name_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalise(a), _normalise(b)).ratio()


class RedundancyChecker:
    """
    Validates a new record against every existing record.
    No external libraries required — pure Python stdlib.
    """

    # Similarity threshold above which two names are considered the same person.
    NAME_THRESHOLD = 0.85

    def is_duplicate(
        self,
        new_record: Dict[str, str],
        existing_records: List[Dict[str, str]],
    ) -> Tuple[bool, str]:
        """
        Returns (True, reason) if the record is a duplicate, else (False, "").
        """
        new_email = _normalise(new_record.get("email", ""))
        new_phone = _clean_phone(new_record.get("phone", ""))
        new_name  = _normalise(new_record.get("name", ""))

        for existing in existing_records:
            ex_email = _normalise(existing.get("email", ""))
            ex_phone = _clean_phone(existing.get("phone", ""))
            ex_name  = _normalise(existing.get("name", ""))

            # ── 1. Exact duplicate ─────────────────────────────────────
            if new_email == ex_email and new_phone == ex_phone and new_name == ex_name:
                return True, f"exact duplicate of record id={existing.get('id', '?')}"

            # ── 2. Email duplicate ─────────────────────────────────────
            if new_email == ex_email:
                return True, f"email '{new_record['email']}' already exists (id={existing.get('id', '?')})"

            # ── 3. Phone duplicate ─────────────────────────────────────
            if new_phone and ex_phone and new_phone == ex_phone:
                return True, (
                    f"phone '{new_record['phone']}' already exists "
                    f"(id={existing.get('id', '?')})"
                )

            # ── 4. Fuzzy name + phone match (probable same person) ─────
            if new_phone and ex_phone and new_phone == ex_phone:
                sim = _name_similarity(new_name, ex_name)
                if sim >= self.NAME_THRESHOLD:
                    return True, (
                        f"likely duplicate — name similarity {sim:.0%}, "
                        f"same phone (id={existing.get('id', '?')})"
                    )

        return False, ""

    # ------------------------------------------------------------------
    # Batch helper: find all duplicates already inside the database
    # ------------------------------------------------------------------

    def find_internal_duplicates(
        self, records: List[Dict[str, str]]
    ) -> List[Tuple[Dict, Dict, str]]:
        """
        Scan a list of records and return all (rec_a, rec_b, reason) pairs
        where rec_b is a duplicate of rec_a.
        Useful for auditing an existing database.
        """
        duplicates = []
        for i, rec in enumerate(records):
            seen_so_far = records[:i]
            is_dup, reason = self.is_duplicate(rec, seen_so_far)
            if is_dup:
                duplicates.append((rec, reason))
        return duplicates
