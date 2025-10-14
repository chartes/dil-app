"""api_utils.py

Utility functions for the API.
"""
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
