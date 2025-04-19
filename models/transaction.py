from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Transaction:
    id: int
    type: str
    from_account: int
    to_account: int
    timestamp: datetime
    from_currency: str
    to_currency: str
    amount: Decimal
    rate: Decimal