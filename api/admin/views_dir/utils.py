"""utils.py

utilities for the admin views
"""
import os
from werkzeug.utils import secure_filename

def prefix_name(_, file_data):
    parts = os.path.splitext(file_data.filename)
    return secure_filename('file-%s%s' % parts)