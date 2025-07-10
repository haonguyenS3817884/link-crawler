from datetime import datetime

def encode_datetime(dt: datetime) -> str:
    """Convert a datetime to its ISO-8601 string."""
    return dt.isoformat()