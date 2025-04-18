from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class Snapshot:
    snapshot_id: int
    account_id: int
    timestamp: datetime
    usd_balance: Decimal
    eur_balance: Decimal
    gbp_balance: Decimal