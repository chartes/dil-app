"""schemas.py

Whoosh schemas for index and full-text search.
"""

from whoosh.fields import (SchemaClass,
                           ID,
                           TEXT,
                           NGRAM,
                           NGRAMWORDS)

class PersonIdxSchema(SchemaClass):
    """Schema for the PersonIdx index."""
    id_dil = ID(stored=True, unique=True)
    lastname = NGRAM(minsize=2, maxsize=15, stored=True)
    firstnames = NGRAM(minsize=2, maxsize=15, stored=True)
    firstnames_lastname = NGRAM(minsize=2, maxsize=30, stored=True)
    content = TEXT(stored=True)
    content_ngram = NGRAMWORDS(minsize=2, maxsize=10, stored=True, field_boost=1.0, tokenizer=None, at='start', queryor=False, sortable=False)