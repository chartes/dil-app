# -*- coding: utf-8 -*-
"""index_utils.py

Whoosh index utils for creating and clearing indexes.
"""

from shutil import rmtree
import bleach
from unidecode import unidecode
from tqdm import tqdm
from whoosh import index
from joblib import Parallel, delayed


def create_store(store: index.FileStorage, path: str) -> None:
    """Create a Whoosh index store at the specified path, clearing any existing index if necessary.

    :param store: The Whoosh FileStorage object representing the index storage.
    :type store: whoosh.filedb.filestore.FileStorage
    :param path: The file system path where the index should be created.
    :type path: str
    :returns: None (the function creates the index store in place)
    :rtype: None
    """
    if index.exists_in(path):
        rmtree(path)
    # print(f"Creating store/index in {path}")
    store.destroy()
    store.create()


def create_index(store: index.FileStorage, schema: index.Schema) -> None:
    """Create a Whoosh index with the given schema in the specified store.

    :param store: The Whoosh FileStorage object representing the index storage.
    :type store: whoosh.filedb.filestore.FileStorage
    :param schema: The Whoosh Schema object defining the structure of the index.
    :type schema: whoosh.fields.Schema
    :returns: None (the function creates the index in place)
    :rtype: None
    """
    store.create_index(schema)


def prepare_content(obj: any) -> str:
    """Prepare content with:
    - personal information
    - professional information
    - patents references

    :param obj: The object containing the information to prepare (e.g., a printer with personal and professional info).
    :type obj: any
    :returns: A cleaned string containing the combined information from the object, suitable for indexing.
    :rtype: str
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


def extract_data(printer: any) -> dict:
    """Extract relevant data from a printer object for indexing.

    :param printer: The printer object containing personal information, professional information, and patents.
    :type printer: any
    :returns: A dictionary with the printer's ID, normalized last name, and combined text
                for indexing.
    :rtype: dict
    """
    content = bleach.clean(
        " ".join(
            [printer.personal_information or "", printer.professional_information or ""]
            + [p.references or "" for p in printer.patents]
        ),
        tags=[],
        attributes=[],
        strip=True,
    )

    return dict(
        id_dil=str(printer._id_dil),
        lastname=unidecode(printer.lastname or "").lower(),
        text=content,
    )


def populate_index(
    session: any, index_: index.Index, model: any, n_jobs: int = -1
) -> index.Index:
    """Populate a Whoosh index with data extracted from a database model.

    :param session: The database session used to query the model.
    :type session: any
    :param index_: The Whoosh index to populate.
    :type index_: whoosh.index.Index
    :param model: The database model to query for data (e.g., a Printer model
                    containing personal and professional information).
    :type model: any
    :param n_jobs: The number of parallel jobs to use for processing documents, defaults to
                    -1 (use all available CPU cores)
    :type n_jobs: int, optional
    :returns: The populated Whoosh index.
    :rtype: whoosh.index.Index
    """
    persons = session.query(model).all()

    serialized_data = [
        extract_data(printer)
        for printer in tqdm(persons, desc="Serializing data for index")
    ]

    def process(doc):
        return dict(
            id_dil=doc["id_dil"],
            lastname=doc["lastname"],
            lastname_exact=doc["lastname"],
            content=doc["text"],
        )

    documents = Parallel(n_jobs=n_jobs)(
        delayed(process)(doc)
        for doc in tqdm(serialized_data, desc="Prepare documents for index")
    )

    with index_.writer() as writer:
        for doc in tqdm(documents, desc="Index documents in Whoosh backend"):
            writer.add_document(**doc)
    return index_
