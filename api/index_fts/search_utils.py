from unidecode import unidecode
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
from whoosh.query import Or, Term
from whoosh import index
from api.index_fts.index_conf import st

from whoosh.qparser import QueryParser, OrGroup, AndGroup
from whoosh.query import Or, Term, And
from unidecode import unidecode




def search_whoosh(query_firstnames_lastname: str = "",
                  query_content: str = "",
                  limit=10000000):
    ix = st.open_index()
    hits = {}

    # Normalisation
    def remove_first_joker(query):
        """Remove the first joker character if present."""
        if query.strip().startswith("*"):
            return query[1:]
        return query

    query_firstnames_lastname = remove_first_joker(unidecode(query_firstnames_lastname.lower().strip())) if query_firstnames_lastname else ""
    query_content = remove_first_joker(query_content.strip()) if query_content else ""

    if not query_firstnames_lastname and not query_content:
        return {}

    with ix.searcher() as searcher:
        # Choix de la requête
        if query_firstnames_lastname and query_content:
            # Requête AND
            parser1 = QueryParser('firstnames_lastname', schema=ix.schema)
            parser2 = QueryParser('content', schema=ix.schema)
            query = And([
                parser1.parse(query_firstnames_lastname),
                parser2.parse(query_content)
            ])
        elif query_firstnames_lastname:
            parser = QueryParser('firstnames_lastname', schema=ix.schema, group=AndGroup)
            query = parser.parse(query_firstnames_lastname)
        elif query_content:
            parser = MultifieldParser(['content'], schema=ix.schema, group=AndGroup)
            query = parser.parse(query_content)

        results = searcher.search(query, limit=limit)
        for r in results:
            highlight = r.highlights("content") if "content" in r else None
            hits[r["id_dil"]] = {"highlight": highlight}

        return hits