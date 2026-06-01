"""
data_validator.py — Input validation before redundancy checking.

Validates:
  • name  — non-empty, 2–100 characters, letters/spaces/hyphens only
  • email — RFC-5321 simplified regex
  • phone — 7–15 digits (E.164 compatible after stripping non-digits)
"""

import re
from typing import Tuple


# Simplified but practical email regex
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

# Accept international phone numbers: optional +, digits, spaces, hyphens, parens
_PHONE_DIGITS_RE = re.compile(r"\d")


class DataValidator:
    """Stateless validator — all methods are pure functions."""

    def validate(self, name: str, email: str, phone: str) -> Tuple[bool, str]:
        """
        Returns (True, "") if all fields are valid.
        Returns (False, reason) on the first failing check.
        """
        ok, msg = self.validate_name(name)
        if not ok:
            return False, msg

        ok, msg = self.validate_email(email)
        if not ok:
            return False, msg

        ok, msg = self.validate_phone(phone)
        if not ok:
            return False, msg

        return True, ""

    # ------------------------------------------------------------------

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        name = name.strip()
        if not name:
            return False, "name is empty"
        if len(name) < 2:
            return False, "name too short (min 2 chars)"
        if len(name) > 100:
            return False, "name too long (max 100 chars)"
        # Allow letters (any language), spaces, hyphens, apostrophes
        if re.search(r"[^a-zA-Z\s\-\'\u00C0-\u024F]", name):
            return False, f"name contains invalid characters: '{name}'"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        email = email.strip()
        if not email:
            return False, "email is empty"
        if not _EMAIL_RE.match(email):
            return False, f"invalid email format: '{email}'"
        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        phone = phone.strip()
        if not phone:
            return False, "phone is empty"
        digits = _PHONE_DIGITS_RE.findall(phone)
        if len(digits) < 7:
            return False, f"phone too short (min 7 digits): '{phone}'"
        if len(digits) > 15:
            return False, f"phone too long (max 15 digits): '{phone}'"
        return True, ""
