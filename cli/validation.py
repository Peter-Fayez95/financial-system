from collections import defaultdict
from decimal import Decimal
import click

VALID_CURRENCIES = ["USD", "EUR", "GBP"]

def parse_currency_list(ctx, param, value):
    """Parses comma-separated CUR=AMT entries into a dict with currency validation."""
    if not value:
        return defaultdict(Decimal)
    currencies = defaultdict(Decimal)
    for pair in value.split(","):
        if "=" not in pair:
            raise click.BadParameter(f"Invalid format: '{pair}', expected CUR=AMT")
        cur, amt = pair.strip().split("=")
        cur = cur.upper()
        if cur not in VALID_CURRENCIES:
            raise click.BadParameter(f"Invalid currency '{cur}'. Must be one of {', '.join(VALID_CURRENCIES)}")
        try:
            currencies[cur] = round(Decimal(amt), 2)
        except ValueError:
            raise click.BadParameter(f"Invalid amount for {cur}: {amt}")
    return currencies


def validate_amount(ctx, param, value):
    if Decimal(value) <= 0:
        raise click.BadParameter(f"The amount must be positive. You provided: {value}")
    return round(Decimal(value), 2)


def validate_rate(ctx, param, value):
    if Decimal(value) <= 0:
        raise click.BadParameter(f"The rate must be positive. You provided: {value}")
    return round(Decimal(value), 2)