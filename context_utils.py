from datetime import datetime
from typing import List, Dict, Any

TIMESTAMP_FORMAT = "[%Y-%m-%d %H:%M:%S]"

def order_in_time(*lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Orders elements from multiple lists based on the timestamp
    embedded in their dictionary keys.
    """

    def extract_timestamp(item: Dict[str, Any]) -> datetime:
        key = next(iter(item.keys()))
        timestamp_str = key.split("]")[0] + "]"
        return datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)

    combined = [item for lst in lists for item in lst]
    return sorted(combined, key=extract_timestamp)