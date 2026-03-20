"""schemas.py

Whoosh schemas for index and full-text search.
"""

from whoosh.fields import SchemaClass, ID, TEXT, NGRAM, KEYWORD


class PersonIdxSchema(SchemaClass):
    id_dil = ID(stored=True, unique=True)
    lastname = NGRAM(minsize=2, maxsize=20, stored=True)
    lastname_exact = KEYWORD(stored=True, lowercase=True, commas=False, scorable=False)
    content = TEXT(stored=True)
