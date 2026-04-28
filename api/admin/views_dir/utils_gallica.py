# -*- coding: utf-8 -*-

"""utils_gallica.py

Utilities for handling Gallica URLs
and converting them to IIIF image URLs.
"""

import re
from urllib.parse import urlparse


GALLICA_HOSTS = {"gallica.bnf.fr", "www.gallica.bnf.fr"}


def _normalize_gallica_url(url: str) -> str:
    """Clean and normalize a Gallica URL to a standard format.
      .../ark:/12148/<id>
      .../ark:/12148/<id>/fXXX
      .../ark:/12148/<id>/fXXX.item

    :param url: The original URL to normalize.
    :type url: str
    :return: A normalized URL in the format .../ark:/12148/<id>
                or .../ark:/12148/<id>/fXXX.item if a folio is present.
    :rtype: str
    """
    if not url:
        return ""

    clean_url = url.strip().split("?")[0].split("#")[0]

    match = re.match(
        r"^(https?://(?:www\.)?gallica\.bnf\.fr/ark:/12148/[^/.?/#]+)(?:/(f\d+)(?:\.item)?)?",
        clean_url,
        flags=re.IGNORECASE,
    )

    if not match:
        return clean_url

    base_ark = match.group(1)
    folio = match.group(2)

    if folio:
        return f"{base_ark}/{folio}.item"
    return base_ark


def is_gallica_url(url: str) -> bool:
    """Check if the given URL is a valid Gallica ARK URL.

    Valid formats include:
    - https://gallica.bnf.fr/ark:/12148/btv1b550
    - https://gallica.bnf.fr/ark:/12148/btv1b52505441p/f226.item
    - https://gallica.bnf.fr/ark:/12148/btv1b101
    - https://gallica.bnf.fr/ark:/12148/btv1b105653893.r=Pau%20%20Statue%20de%20Henri%20IV?rk=193134;0

    :param url: The URL to check.
    :type url: str
    :return: True if the URL is a valid Gallica ARK URL, False otherwise
    :rtype: bool
    """
    if not url:
        return False

    try:
        clean_url = _normalize_gallica_url(url)
        parsed = urlparse(clean_url)
        return parsed.netloc.lower() in GALLICA_HOSTS and "/ark:/12148/" in parsed.path
    except Exception:
        return False


def gallica_url_to_iiif(url: str, width: int = 1000) -> str:
    """Convert a Gallica ARK URL to a IIIF image URL for the specified width.
    Supported input formats include:
    - https://gallica.bnf.fr/ark:/12148/btv1b55002798b
    - https://gallica.bnf.fr/ark:/12148/btv1b52505441p/f226.item
    - https://gallica.bnf.fr/ark:/12148/btv1b101228544/f1.item.r=menu%20menu
    - https://gallica.bnf.fr/ark:/12148/btv1b105653893.r=Pau%20%20Statue%20de%20Henri%20IV?rk=193134;0

    :param url: The original Gallica ARK URL to convert.
    :type url: str
    :param width: The desired width of the IIIF image (default is 1000
                    pixels).
    :type width: int
    :return: A IIIF image URL corresponding to the given Gallica ARK URL.
    :rtype: str
    """
    clean_url = _normalize_gallica_url(url)

    if not is_gallica_url(clean_url):
        raise ValueError("URL Gallica invalide.")

    m = re.match(
        r"^https?://(?:www\.)?gallica\.bnf\.fr/(ark:/12148/[^/]+)(?:/(f\d+)(?:\.item)?)?$",
        clean_url,
        flags=re.IGNORECASE,
    )
    if not m:
        raise ValueError(
            "Format d'URL Gallica non pris en charge. "
            "Attendu : .../ark:/12148/... ou .../ark:/12148/.../fXXX.item"
        )

    ark = m.group(1)
    folio = m.group(2) or "f1"

    return f"https://gallica.bnf.fr/iiif/{ark}/{folio}/full/{width},/0/native.jpg"
