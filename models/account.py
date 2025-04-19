from decimal import Decimal
from typing import DefaultDict
from dataclasses import dataclass


@dataclass
class Account:
    id: int
    usd_balance: Decimal
    eur_balance: Decimal
    gbp_balance: Decimal
