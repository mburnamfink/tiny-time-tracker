from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


_HM_RE = re.compile(r"^(?:(\d+)h)?(?:(\d+)m)?$")


def parse_hours(raw: str) -> float:
    """Parse `1.5`, `1h30m`, or `90m` into decimal hours. No rounding applied."""
    s = raw.strip().lower()
    if not s:
        raise ValueError("no hours given")
    try:
        return float(s)
    except ValueError:
        pass
    m = _HM_RE.match(s)
    if not m or (m.group(1) is None and m.group(2) is None):
        raise ValueError(f"cannot parse hours from {raw!r} (use e.g. 1.5, 1h30m, 90m)")
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    return hours + minutes / 60


_NEG_INT_RE = re.compile(r"^-\d+$")


def parse_date(raw: str, today: date | None = None) -> date:
    """Parse `--date`: a negative integer (days ago) or an ISO 8601 date. Else reject."""
    today = today or date.today()
    s = raw.strip()
    if _NEG_INT_RE.match(s):
        return today - timedelta(days=abs(int(s)))
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise ValueError(
            f"cannot parse date from {raw!r} (use a negative integer like -2, or an ISO date like 2026-08-09)"
        )
