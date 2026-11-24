"""The single audited money module (BLUEPRINT Doc 3.1, Doc 9.7).

All money is integer paise. This module never uses floating point: parsing is
done on the decimal string, and formatting uses integer division only.
"""

import re
from typing import NewType

Paise = NewType("Paise", int)

PAISE_PER_RUPEE = 100

# Optional sign, digits with optional thousands commas, optional 1-2 decimals.
# Only ASCII digits are accepted ("\d" would also match other scripts' digits).
_AMOUNT_RE = re.compile(r"^([+-]?)([0-9]+(?:,[0-9]+)*)(?:\.([0-9]{1,2}))?$")


def ensure_paise(value: object) -> Paise:
    """Accept only a real int (not bool, not float, not Decimal) as paise."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"money must be int paise, got {type(value).__name__}")
    return Paise(value)


def from_rupees(rupees: int) -> Paise:
    """Whole rupees to paise. Fractional rupees must go through parse_inr."""
    return Paise(ensure_paise(rupees) * PAISE_PER_RUPEE)


def parse_inr(text: str) -> Paise:
    """Parse an amount string such as "1,23,456.78" into paise (12345678).

    Accepts Indian or Western comma grouping (bank statements use both), an
    optional sign and at most two decimal places. More than two decimals is an
    error rather than a silent rounding. Currency symbols are not accepted;
    callers strip them first.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected str, got {type(text).__name__}")
    match = _AMOUNT_RE.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"not a valid amount: {text!r}")
    sign, whole, fraction = match.groups()
    rupees = int(whole.replace(",", ""))
    paise = int((fraction or "").ljust(2, "0"))
    total = rupees * PAISE_PER_RUPEE + paise
    return Paise(-total if sign == "-" else total)


def _group_indian(digits: str) -> str:
    """'12345678' -> '1,23,45,678' (last three digits, then pairs)."""
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    pairs: list[str] = []
    while len(head) > 2:
        pairs.insert(0, head[-2:])
        head = head[:-2]
    pairs.insert(0, head)
    return ",".join(pairs) + "," + tail


def format_inr(paise: int, *, grouping: bool = True) -> str:
    """Format paise as a rupee string with two decimals.

    format_inr(12345678)                 -> "1,23,456.78"
    format_inr(12345678, grouping=False) -> "123456.78"   (e.g. UPI `am`, CSV)
    No currency symbol is added; display layers decide that.
    """
    value = ensure_paise(paise)
    sign = "-" if value < 0 else ""
    rupees, rem = divmod(abs(value), PAISE_PER_RUPEE)
    whole = _group_indian(str(rupees)) if grouping else str(rupees)
    return f"{sign}{whole}.{rem:02d}"
