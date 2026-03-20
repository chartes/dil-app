# -*- coding: utf-8 -*-
"""search_utils.py

Utilities for searching the Whoosh index with normalized queries and handling results.
"""

import re
from html import escape
from unidecode import unidecode

from whoosh.qparser import QueryParser, AndGroup, OrGroup, MultifieldParser
from whoosh.query import And
from whoosh.highlight import HtmlFormatter, ContextFragmenter

from api.index_fts.index_conf import st


def extract_quoted_phrases(query: str) -> list[str]:
    """Extrait les phrases entre guillemets doubles."""
    if not query:
        return []
    return [m.strip() for m in re.findall(r'"([^"]+)"', query) if m.strip()]


def build_phrase_only_highlight(
    content: str, phrases: list[str], context: int = 90
) -> str:
    """Construit un extrait avec highlight exact des phrases, sans surligner les mots isolés."""
    if not content or not phrases:
        return None

    lower_content = content.lower()

    # trouver la première occurrence de n'importe quelle phrase
    first_match = None
    first_phrase = None
    for phrase in phrases:
        idx = lower_content.find(phrase.lower())
        if idx != -1 and (first_match is None or idx < first_match):
            first_match = idx
            first_phrase = phrase

    if first_match is None:
        return None

    start = max(0, first_match - context)
    end = min(len(content), first_match + len(first_phrase) + context)
    snippet = content[start:end]

    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."

    # échapper HTML puis surligner uniquement les phrases exactes
    snippet_escaped = escape(snippet)

    for phrase in sorted(phrases, key=len, reverse=True):
        pattern = re.compile(re.escape(escape(phrase)), flags=re.IGNORECASE)
        snippet_escaped = pattern.sub(
            lambda m: f"<mark>{m.group(0)}</mark>", snippet_escaped
        )

    return snippet_escaped


def search_whoosh(query_lastname: str = "", query_content: str = "", limit: int = 5000):
    ix = st.open_index()
    hits = {}

    raw_query_content = query_content or ""

    def remove_first_joker(query: str) -> str:
        if query and query.strip().startswith("*"):
            return query.strip()[1:]
        return query.strip()

    query_lastname = (
        remove_first_joker(unidecode(query_lastname.lower().strip()))
        if query_lastname
        else ""
    )
    query_content = remove_first_joker(query_content.strip()) if query_content else ""

    quoted_phrases = extract_quoted_phrases(raw_query_content)

    if not query_lastname and not query_content:
        return {}

    with ix.searcher() as searcher:
        if query_lastname and query_content:
            parser1 = QueryParser("lastname", schema=ix.schema, group=AndGroup)
            parser2 = MultifieldParser(["content"], schema=ix.schema, group=OrGroup)

            q1 = parser1.parse(query_lastname)
            q2 = parser2.parse(query_content)
            query = And([q1, q2])

        elif query_lastname:
            parser = QueryParser("lastname", schema=ix.schema, group=AndGroup)
            query = parser.parse(query_lastname)

        else:
            parser = MultifieldParser(["content"], schema=ix.schema, group=OrGroup)
            query = parser.parse(query_content)

        results = searcher.search(query, limit=limit, terms=True)
        results.fragmenter = ContextFragmenter(surround=60)
        results.formatter = HtmlFormatter(tagname="mark")
        for r in results:
            highlight = None
            try:
                if quoted_phrases and "content" in r:
                    highlight = build_phrase_only_highlight(
                        r["content"], quoted_phrases
                    )
                else:
                    highlight = r.highlights("content")
            except Exception:
                highlight = None

            hits[r["id_dil"]] = {"highlight": highlight}

    ix.close()
    return hits
