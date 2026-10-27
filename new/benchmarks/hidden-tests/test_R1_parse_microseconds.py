"""Hidden evaluation tests for R1: copied to tests/hidden/ in a disposable copy of parse."""

import parse


def test_hidden_time_only_format_keeps_microseconds():
    assert parse.parse("{:tt}", "10:21:36.000249")[0].microsecond == 249


def test_hidden_global_date_format_keeps_microseconds():
    assert parse.parse("{:tg}", "20/1/1972 10:21:36.000502")[0].microsecond == 502


def test_hidden_iso_values_that_float_rounding_corrupts():
    for digits in ("000991", "000507", "501902"):
        assert parse.parse("{:ti}", f"2023-10-14T15:09:08.{digits}Z")[0].microsecond == int(digits)


def test_hidden_extra_digits_are_truncated_not_rounded():
    assert parse.parse("{:ti}", "2023-10-14T15:09:08.9999999Z")[0].microsecond == 999999
