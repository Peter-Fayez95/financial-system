from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CurrencyExchange:
    id: int
    timestamp: datetime
    from_currency: str
    to_currency: str
    rate: Decimal