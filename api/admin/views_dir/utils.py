# -*- coding: utf-8 -*-

"""utils.py

utilities for the admin views
"""

import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from unidecode import unidecode


def prefix_name(_, file_data: object) -> str:
    """Prefix the filename with 'file-' and ensure it is secure.

    :param _: Unused parameter (required by Flask-Admin file upload interface)
    :type _: object
    :param file_data: The file data object containing the original filename.
    :type file_data: object
    :return: A secure filename prefixed with 'file-'.
    :rtype: str
    """
    parts = os.path.splitext(file_data.filename)
    return secure_filename("file-%s%s" % parts)


def get_search_filter(column: object, search: str, dialect_name: str) -> object:
    """Get a SQLAlchemy filter for searching a column with a case-insensitive, accent-insensitive match.

    :param column: The SQLAlchemy column to search.
    :type column: object
    :param search: The search string to match against the column.
    :type search: str
    :param dialect_name: The name of the database dialect (e.g., 'postgresql', 'mysql').
    :type dialect_name: str
    :return: A SQLAlchemy filter expression for the search.
    :rtype: object
    """
    normalized_search = unidecode(search).lower()
    return func.lower(column).like(f"%{normalized_search}%")
