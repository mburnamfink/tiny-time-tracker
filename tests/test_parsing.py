from __future__ import annotations

from datetime import date

import pytest

from tt.parsing import parse_date, parse_hours, slugify


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1.5", 1.5),
        ("1h30m", 1.5),
        ("90m", 1.5),
        ("2", 2.0),
        ("2h", 2.0),
        ("0.25", 0.25),
        ("15m", 0.25),
    ],
)
def test_parse_hours(raw, expected):
    assert parse_hours(raw) == pytest.approx(expected)


@pytest.mark.parametrize("raw", ["", "abc", "1x", "h", "m", "1h30"])
def test_parse_hours_rejects(raw):
    with pytest.raises(ValueError):
        parse_hours(raw)


def test_parse_date_negative_int():
    today = date(2026, 8, 10)
    assert parse_date("-1", today=today) == date(2026, 8, 9)
    assert parse_date("-2", today=today) == date(2026, 8, 8)


def test_parse_date_iso():
    assert parse_date("2026-08-09") == date(2026, 8, 9)


@pytest.mark.parametrize("raw", ["2", "1", "tomorrow", "08-09", "2026/08/09", "0.5"])
def test_parse_date_rejects(raw):
    with pytest.raises(ValueError):
        parse_date(raw)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Book Review", "book-review"),
        ("BookReview", "bookreview"),
        ("book_review", "book-review"),
        ("  admin  ", "admin"),
        ("Project  Ludic", "project-ludic"),
    ],
)
def test_slugify(raw, expected):
    assert slugify(raw) == expected
