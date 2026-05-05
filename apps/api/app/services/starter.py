"""Sourdough starter peak estimation.

peak_hours = peak_base_hours * 2^((20 - kitchen_temp_c) / 10)

At 20°C, peak_hours = base (e.g. 6 hours).
At 30°C, peak_hours = base * 0.5 (faster).
At 10°C, peak_hours = base * 2 (slower).
"""

from datetime import datetime, timedelta
from decimal import Decimal


def estimate_peak(
    peak_base_hours: Decimal,
    kitchen_temp_c: Decimal,
    fed_at: datetime,
) -> datetime:
    """Estimate when a starter will peak given feeding time and temperature."""
    base = float(peak_base_hours)
    temp = float(kitchen_temp_c)
    peak_hours = base * (2 ** ((20 - temp) / 10))
    return fed_at + timedelta(hours=peak_hours)
