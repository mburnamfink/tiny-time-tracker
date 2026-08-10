from __future__ import annotations

import difflib
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


def suggest_similar(category: str, known: list[str], n: int = 3, cutoff: float = 0.6) -> list[str]:
    """Close matches to `category` among `known`, for a typo warning. Empty when `category`
    is already known or nothing is close enough — i.e. when no warning should be shown."""
    if category in known:
        return []
    return difflib.get_close_matches(category, known, n=n, cutoff=cutoff)
