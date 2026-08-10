from __future__ import annotations

from collections import Counter
from pathlib import Path

from .store import read_entries


def category_counts(store_path: Path) -> Counter[str]:
    """Count entries per category across the whole store."""
    return Counter(e["category"] for e in read_entries(store_path) if e.get("category"))


def known_categories(store_path: Path) -> list[str]:
    """Distinct categories present in the store, sorted. This is the known set — there is
    no curated config list; the vocabulary is whatever has been logged so far."""
    return sorted(category_counts(store_path))
