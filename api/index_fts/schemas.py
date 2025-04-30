"""schemas.py

Whoosh schemas for index and full-text search.
"""

from whoosh.fields import (SchemaClass,
                           ID,
                           TEXT)


class PersonIdxSchema(SchemaClass):
    """Schema for the PersonIdx index."""
    id_dil = ID(stored=True, unique=True)
    lastname = TEXT(stored=True)
    firstnames = TEXT(stored=True)
    content = TEXT(stored=True)