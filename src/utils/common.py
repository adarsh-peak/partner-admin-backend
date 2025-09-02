from datetime import datetime
from typing import Optional

def parse_date_string(date_str: Optional[str]) -> Optional[datetime]:
    """
    Try to parse a date string in multiple formats.
    Returns a datetime object if successful, otherwise None.
    """
    if isinstance(date_str, datetime):
        return date_str
    if not date_str:
        return None

    formats = ["%m-%d-%Y", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None

def safe_int(value: str, default: int = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default