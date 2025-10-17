"""api_utils.py

Utility functions for the API.
"""
from typing import Union
import calendar
import re

_COMMA_FIX = re.compile(r'\s*,+\s*')
_MULTI_SPACE = re.compile(r'\s{2,}')

def normalize_firstnames(v: str) -> str:
    """Normalize firstnames by removing extra spaces and fixing commas.

    Examples:
    >>> normalize_firstnames("  Auguste,Titus  ")
    'Auguste, Titus'
    >>> normalize_firstnames("  Auguste ,  Titus  ")
    'Auguste, Titus'
    >>> normalize_firstnames("  Auguste  , Titus, ")
    'Auguste, Titus'
    >>> normalize_firstnames(None)
    None

    :param v: The input string to normalize.
    :type v: str | None
    :return: The normalized string or None if input is None.
    :rtype: str | None
    """
    if not v:
        return v
    s1 = v.strip()
    s = _COMMA_FIX.sub(', ', s1)   # "Auguste,Titus" -> "Auguste, Titus" ; "Auguste ,  Titus" -> "Auguste, Titus"
    s = re.sub(r',\s*$', '', s)   # remove final comma
    s = _MULTI_SPACE.sub(' ', s)  # remove multiple spaces
    #print(s1," > ", s, " : ", s == s1)
    return s

def normalize_date(date_str: str) -> str:
    """Normalize date strings to 'YYYY-MM-DD' format.
    Handles partial dates and removes approximation symbols.

    Examples:
    >>> normalize_date("2020")
    '2020-01-01'
    >>> normalize_date("2020-05")
    '2020-05-01'
    >>> normalize_date("2020-05-15")
    '2020-05-15'
    >>> normalize_date("~2020-05-15")
    '2020-05-15'

    :param date_str: The input date string.
    :type date_str: str
    :return: The normalized date string.
    :rtype: str
    """
    date_str = date_str.replace("~", "")
    parts = date_str.split("-")
    if len(parts) == 1:
        return f"{parts[0]}-01-01"
    elif len(parts) == 2:
        return f"{parts[0]}-{parts[1]}-01"
    return date_str


def year_bounds(year_str: str) -> Union[tuple[str, str], None]:
    """Converts 'YYYY' or 'YYYY-..' to (PSTART, PEND) ISO.

    :param year_str: Year string, e.g. '1855' or '1855-..'
    :type year_str: str
    :return: Tuple of (PSTART, PEND) in ISO format.
    :rtype: Union[tuple[str, str], None]
    """
    y = int(year_str[:4])  # ok with '1855' or '1855-..'
    return f"{y}-01-01", f"{y}-12-31"

DATE_Y   = re.compile(r"^\d{4}$")
DATE_YM  = re.compile(r"^\d{4}-\d{2}$")
DATE_YMD = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def period_bounds(s: str) -> Union[tuple[str, str], tuple[None, None]]:
    """Converts a date string to (PSTART, PEND) ISO format.
    Handles 'YYYY', 'YYYY-MM', 'YYYY-MM-DD' and partial matches.

    :param s: Date string.
    :type s: str
    :return: Tuple of (PSTART, PEND) in ISO format or (None, None) if invalid.
    :rtype: Union[tuple[str, str], tuple[None, None]]
    """
    s = (s or "").strip()
    if DATE_YMD.match(s):
        return s, s
    if DATE_YM.match(s):
        y, m = map(int, s.split("-"))
        last_day = calendar.monthrange(y, m)[1]
        return f"{y:04d}-{m:02d}-01", f"{y:04d}-{m:02d}-{last_day:02d}"
    if DATE_Y.match(s):
        y = int(s)
        return f"{y:04d}-01-01", f"{y:04d}-12-31"
    if len(s) >= 7 and DATE_YM.match(s[:7]):
        y, m = map(int, s[:7].split("-"))
        last_day = calendar.monthrange(y, m)[1]
        return f"{y:04d}-{m:02d}-01", f"{y:04d}-{m:02d}-{last_day:02d}"
    if len(s) >= 4 and DATE_Y.match(s[:4]):
        y = int(s[:4])
        return f"{y:04d}-01-01", f"{y:04d}-12-31"
    return None, None
