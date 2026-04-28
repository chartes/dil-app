# -*- coding: utf-8 -*-

"""utils.py

utilities for the admin views
"""

import os
from unidecode import unidecode

from werkzeug.utils import secure_filename
from sqlalchemy import func
from flask import render_template_string


def render_popup_response(field_id: str, obj_id: int, obj_text: str) -> str:
    """Render a response for a popup form submission, sending a message back to the parent window.

    :param field_id: The ID of the form field that was updated.
    :type field_id: str
    :param obj_id: The ID of the newly created object.
    :type obj_id: int
    :param obj_text: The text representation of the newly created object.
    :type obj_text: str
    :return: An HTML response that sends a message to the parent window indicating the success of
                the creation of the related object.
    :rtype: str
    """
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head><meta charset="utf-8"></head>
        <body>
            <script>
                window.parent.postMessage({
                    type: "admin:create-related-success",
                    message: {{ message|tojson }}
                }, window.location.origin);
            </script>
        </body>
        </html>
        """,
        message=f'"{obj_text}" a bien été ajouté au référentiel.',
    )


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
