import pytest
from click import BadParameter
from decimal import Decimal
from collections import defaultdict
from cli.validation import parse_currency_list, validate_amount, validate_rate


# parse_currency_list
def test_parse_currency_list_valid():
    result = parse_currency_list(None, None, "USD=100.50,EUR=200")
    expected = defaultdict(
        Decimal, {"USD": Decimal("100.50"), "EUR": Decimal("200.00")}
    )
    assert result == expected
    assert isinstance(result["USD"], Decimal)
    assert isinstance(result["EUR"], Decimal)


def test_parse_currency_list_empty():
    result = parse_currency_list(None, None, "")
    assert result == defaultdict(Decimal)


def test_parse_currency_list_invalid_format():
    with pytest.raises(BadParameter, match="Invalid format: 'USD:100'"):
        parse_currency_list(None, None, "USD:100")


def test_parse_currency_list_invalid_currency():
    with pytest.raises(BadParameter, match="Invalid currency 'JPY'"):
        parse_currency_list(None, None, "USD=100,JPY=50")


def test_parse_currency_list_invalid_amount():
    with pytest.raises(BadParameter, match="Invalid amount for USD: abc"):
        parse_currency_list(None, None, "USD=abc")


# validate_amount
def test_validate_amount_valid():
    assert validate_amount(None, None, "123.45") == Decimal("123.45")
    assert validate_amount(None, None, 100) == Decimal(
        "100.00"
    )  # Test float conversion


def test_validate_amount_zero():
    with pytest.raises(BadParameter, match="must be positive"):
        validate_amount(None, None, "0")


def test_validate_amount_negative():
    with pytest.raises(BadParameter, match="must be positive"):
        validate_amount(None, None, "-10.5")


def test_validate_amount_precision():
    assert validate_amount(None, None, "123.456") == Decimal("123.46")
    assert validate_amount(None, None, 100.005) == Decimal("100.00")
    assert validate_amount(None, None, 100.015) == Decimal("100.02")


# validate_rate
def test_validate_rate_valid():
    assert validate_rate(None, None, "1.2345") == Decimal("1.23")
    assert validate_rate(None, None, 0.05) == Decimal("0.05")  # Test float conversion


def test_validate_rate_zero():
    with pytest.raises(BadParameter, match="must be positive"):
        validate_rate(None, None, "0")


def test_validate_rate_negative():
    with pytest.raises(BadParameter, match="must be positive"):
        validate_rate(None, None, "-0.5")


def test_validate_rate_precision():
    assert validate_rate(None, None, "1.235") == Decimal("1.24")  # Rounds up
    assert validate_rate(None, None, "1.234") == Decimal("1.23")  # Rounds down
    assert validate_rate(None, None, 0.005) == Decimal("0.01")  # Rounds up near zero
    assert validate_rate(None, None, 0.004) == Decimal("0.00")  # Rounds down near zero


def test_validate_rate_invalid_input():
    with pytest.raises(Exception):  # Catches Decimal InvalidOperation
        validate_rate(None, None, "abc")
