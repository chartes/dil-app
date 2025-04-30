"""index_utils.py

Whoosh index utils for creating and clearing indexes.
"""
from shutil import rmtree
import bleach

from whoosh import index


def create_store(store, path) -> None:
    if index.exists_in(path):
        rmtree(path)
    # print(f"Creating store/index in {path}")
    store.destroy()
    store.create()


def create_index(store, schema) -> index:
    store.create_index(schema)


def populate_index(session, index_, model):
    persons = session.query(model).all()
    writer = index_.writer()
    for printer in persons:
        texts = [
            printer.personal_information or "",
            printer.professional_information or "",
        ]
        sources = []
        for patent in printer.patents:
            sources.append(patent.references or "")

        all_text = " ".join(texts + sources)
        clean_text = bleach.clean(all_text, tags=[], attributes=[], strip=True)

        lastname = printer.lastname or ""
        firstnames = printer.firstnames or ""

        writer.add_document(id_dil=str(printer._id_dil),
                            lastname=lastname,
                            firstnames=firstnames,
                            content=clean_text)

    writer.commit()
    return index_