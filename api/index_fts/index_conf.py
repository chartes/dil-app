import os
import sys
from whoosh.filedb.filestore import FileStorage

from api.config import (BASE_DIR,
                        settings)

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)

# Initialize storage and index
st = FileStorage(WHOOSH_INDEX_DIR)