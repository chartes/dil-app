"""utils.py

utilities for the admin views
"""
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from unidecode import unidecode
import unicodedata

def prefix_name(_, file_data):
    parts = os.path.splitext(file_data.filename)
    return secure_filename('file-%s%s' % parts)

def get_search_filter(column, search, dialect_name):
    normalized_search = unidecode(search).lower()
    return func.lower(column).like(f"%{normalized_search}%")