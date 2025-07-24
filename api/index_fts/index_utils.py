"""index_utils.py

Whoosh index utils for creating and clearing indexes.
"""
from shutil import rmtree
import bleach
from unidecode import unidecode
from tqdm import tqdm
from whoosh import index
from joblib import Parallel, delayed


def create_store(store, path) -> None:
    if index.exists_in(path):
        rmtree(path)
    # print(f"Creating store/index in {path}")
    store.destroy()
    store.create()


def create_index(store, schema) -> index:
    store.create_index(schema)

def prepare_content(obj):
    """Prepare content with:
    - personal information
    - professional information
    """
    texts = [
        obj.personal_information or "",
        obj.professional_information or "",
    ]
    sources = []
    for patent in obj.patents:
        sources.append(patent.references or "")

    all_text = " ".join(texts + sources)
    clean_text = bleach.clean(all_text, tags=[], attributes=[], strip=True)
    return clean_text


def extract_data(printer):
    """Extraction safe des données sans session SQLAlchemy"""
    content = bleach.clean(
                " ".join([
                    printer.personal_information or "",
                    printer.professional_information or ""
                ] + [p.references or "" for p in printer.patents]),
                tags=[], attributes=[], strip=True
            )

    return dict(
        id_dil=str(printer._id_dil),
        lastname=unidecode(printer.lastname or "").lower(),
        firstnames=unidecode(printer.firstnames or "").lower(),
        clean_text=unidecode(
            content
        ).lower(),
        text=content,
    )

def populate_index(session, index_, model, n_jobs=-1):
    persons = session.query(model).all()

    serialized_data = [extract_data(printer) for printer in tqdm(persons, desc="Serializing data for index")]

    def process(doc):
        return dict(
            id_dil=doc['id_dil'],
            lastname=doc['lastname'],
            firstnames=doc['firstnames'],
            firstnames_lastname=f"{' '.join(doc['firstnames'].split(','))} {doc['lastname']}",
            content=doc['text'],
            content_ngram=doc['clean_text'],
        )

    documents = Parallel(n_jobs=n_jobs)(
        delayed(process)(doc) for doc in tqdm(serialized_data, desc="Prepare documents for index")
    )

    with index_.writer() as writer:
        for doc in tqdm(documents, desc="Index documents in Whoosh backend"):
            writer.add_document(**doc)
    return index_