from whoosh.qparser import MultifieldParser
from whoosh import index
from api.index_fts.index_conf import st

def search_whoosh(keyword, fields=["content"], limit=50):
    """
    Recherche plein texte dans un ou plusieurs champs (Whoosh).

    :param keyword: le terme recherché
    :param fields: liste de champs sur lesquels faire la recherche (par défaut: ["content"])
    :param limit: nombre maximum de résultats
    :return: liste de dicts avec id_dil et highlights
    """
    ix = st.open_index()
    with ix.searcher() as searcher:
        parser = MultifieldParser(fields, ix.schema)
        q = parser.parse(keyword)
        results = searcher.search(q, limit=limit)

        hits = []
        for r in results:
            # Try to highlight the first matching field (fallback on 'content')
            highlight = None
            for field in fields:
                if field in r:
                    highlight = r.highlights(field)
                    if highlight:
                        break

            hits.append({
                "id_dil": r["id_dil"],
                "highlight": highlight or ""  # fallback to empty if nothing
            })

        return hits