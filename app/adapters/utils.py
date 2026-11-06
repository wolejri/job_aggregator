from datetime import datetime, timezone
from dateutil import parser as date_parser
import requests
TIMEOUT = 20
HEADERS = {"User-Agent": "ResumeJobAggregator/1.0 (personal job discovery tool)"}
def parse_date(value):
    if value in (None, ""): return None
    try:
        if isinstance(value, (int, float)): return datetime.fromtimestamp(value, tz=timezone.utc)
        parsed = date_parser.parse(str(value))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError): return None
def get_json(url, params=None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()
def remote_arrangement(text, explicit_remote=False, explicit_hybrid=False):
    value = (text or "").lower()
    if explicit_hybrid or "hybrid" in value: return "hybrid"
    if explicit_remote or "remote" in value or "work from home" in value: return "remote"
    if any(x in value for x in ("on-site", "onsite", "on site", "office-based")): return "onsite"
    return "unknown"
def country_codes(text):
    value = (text or "").lower()
    mapping = {"canada":"CA", "canadian":"CA", "united states":"US", "usa":"US", "u.s.":"US", "mexico":"MX"}
    return sorted({code for phrase, code in mapping.items() if phrase in value})
