from datetime import datetime

from src.time_format import format_timestamp


def _dt(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, 0)


def test_12h_format_morning():
    dt = _dt(2026, 6, 6, 8, 6)
    result = format_timestamp(dt, use_24h=False)
    assert result == "6/6/2026 8:06 AM"


def test_12h_format_afternoon():
    dt = _dt(2026, 6, 6, 20, 6)
    result = format_timestamp(dt, use_24h=False)
    assert result == "6/6/2026 8:06 PM"


def test_12h_format_midnight():
    dt = _dt(2026, 6, 6, 0, 0)
    result = format_timestamp(dt, use_24h=False)
    assert result == "6/6/2026 12:00 AM"


def test_12h_format_noon():
    dt = _dt(2026, 6, 6, 12, 0)
    result = format_timestamp(dt, use_24h=False)
    assert result == "6/6/2026 12:00 PM"


def test_24h_format():
    dt = _dt(2026, 6, 6, 20, 6)
    result = format_timestamp(dt, use_24h=True)
    assert result == "6/6/2026 20:06"


def test_24h_format_midnight():
    dt = _dt(2026, 6, 6, 0, 5)
    result = format_timestamp(dt, use_24h=True)
    assert result == "6/6/2026 0:05"


def test_24h_format_single_digit_month():
    dt = _dt(2026, 1, 9, 14, 30)
    result = format_timestamp(dt, use_24h=True)
    assert result == "1/9/2026 14:30"


def test_12h_format_leading_zero_minute():
    dt = _dt(2026, 12, 25, 9, 3)
    result = format_timestamp(dt, use_24h=False)
    assert result == "12/25/2026 9:03 AM"


def test_naive_datetime_uses_as_is():
    dt = _dt(2026, 3, 15, 10, 30)
    result_12h = format_timestamp(dt, use_24h=False)
    result_24h = format_timestamp(dt, use_24h=True)
    assert result_12h == "3/15/2026 10:30 AM"
    assert result_24h == "3/15/2026 10:30"
