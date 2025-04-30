import os
import sys

from whoosh.filedb.filestore import FileStorage

from api.config import (BASE_DIR,
                        settings)
from api.index_fts.schemas import PersonIdxSchema
from api.index_fts.index_utils import (create_store,
                                       create_index,
                                       populate_index)

from api.models.models import Person
from api.database import session

WHOOSH_INDEX_DIR = os.path.join(BASE_DIR, settings.WHOOSH_INDEX_DIR)

# Initialize storage and index
st = FileStorage(WHOOSH_INDEX_DIR)

def index_create():
    """Create the index for full-text search. (Whoosh)"""
    print("Creating the index dir to manage full-text search...")
    try:
        create_store(st, WHOOSH_INDEX_DIR)
        create_index(st, PersonIdxSchema)
        print("✔️The index has been created and ready to populate.")
    except Exception as e:
        print("❌The index has not been created.")
        print(f"Error: {e}")
        sys.exit(1)


def index_populate():
    """Populate index with db data.
    Normally, don't use this command, because using triggers and events
    with db-populate."""
    try:
        ix = st.open_index()
        populate_index(session, ix, Person)
        print("✔️The index has been populated.")
    except Exception as e:
        print("❌The index has not been populated.")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    index_create()
    index_populate()