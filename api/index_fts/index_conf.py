# -*- coding: utf-8 -*-
"""index_conf.py

Configuration for Whoosh full-text search indexing, including the index directory and storage initialization.
"""

import os
from whoosh.filedb.filestore import FileStorage

from api.config import BASE_DIR, settings

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)

# Initialize storage and index
st = FileStorage(WHOOSH_INDEX_DIR)
