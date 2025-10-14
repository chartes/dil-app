"""api_utils.py

Utility functions for the API.
"""
import re

_COMMA_FIX = re.compile(r'\s*,+\s*')
_MULTI_SPACE = re.compile(r'\s{2,}')

def normalize_firstnames(v: str | None) -> str | None:
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
    """
    if not v:
        return v
    s1 = v.strip()
    s = _COMMA_FIX.sub(', ', s1)   # "Auguste,Titus" -> "Auguste, Titus" ; "Auguste ,  Titus" -> "Auguste, Titus"
    s = re.sub(r',\s*$', '', s)   # remove final comma
    s = _MULTI_SPACE.sub(' ', s)  # remove multiple spaces
    #print(s1," > ", s, " : ", s == s1)
    return s