# -*- coding: utf-8 -*-
# /usr/bin/env python3
"""
Script to create the database and import data from TSV files.
"""

import os
import argparse

from contextlib import contextmanager
from sqlalchemy import create_engine

import pandas as pd
import numpy as np

from scripts.dil_dtypes_spec import DTYPE_SPEC
from api.models.models import *

__prefix_model__ = "dil"
__version__ = "1.0.0"


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def load_tsv_to_db(file_path, table_model):
    try:
        with get_session() as session:
            print(f"==> Loading data from {file_path} to {table_model.__tablename__} table.")

            data = pd.read_csv(file_path, sep='\t', encoding='utf-8',
                               dtype=DTYPE_SPEC.get(table_model.__tablename__, None))

            data = data.replace({np.nan: None})

            if '_id_dil' not in data.columns:
                data.insert(0, '_id_dil', None)

            data['_id_dil'] = data['_id_dil'].apply(
                lambda x: x if x else generate_random_uuid(prefix=table_model.__prefix__, provider="dil")
            )

            records = data.to_dict(orient='records')

            session.bulk_insert_mappings(table_model, records)

            print(f"==> {len(records)} rows inserted in {table_model.__tablename__} table.")

    except FileNotFoundError as e:
        print(f"Erreur : Fichier introuvable : {file_path}")

    except Exception as e:
        print(f"Erreur lors de l'importation dans la table {table_model.__tablename__}: {e}")


if __name__ == "__main__":
    # constants
    base_path_data_tables = "../data/tables_to_migrate/final_rev/tables/"
    base_path_data_relations = "../data/tables_to_migrate/final_rev/relations/"
    # get arguments from command line
    parser = argparse.ArgumentParser(description="Create the database and import data from TSV files.")
    parser.add_argument("--db", help="Database path and name", default=f"{__prefix_model__}_{__version__}.db")

    args = parser.parse_args()
    db_name = args.db
    current_dir = os.path.dirname(__file__)

    if db_name == f"dil_{__version__}.db":
        db_path = os.path.join(current_dir, "../db", db_name)
        print(f"==> Database path: {db_path}")
    else:
        db_path = db_name
        print(f"==> Database path: {db_path}")

    engine = create_engine(f"sqlite:///{db_path}", echo=True)

    BASE.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    base_path_data_tables = os.path.join(current_dir, base_path_data_tables)
    base_path_data_relations = os.path.join(current_dir, base_path_data_relations)

    ORDER_IMPORT = [
        (f'{base_path_data_tables}table_city.tsv', City),
        (f'{base_path_data_tables}table_address.tsv', Address),
        (f'{base_path_data_tables}table_person.tsv', Person),
        (f'{base_path_data_tables}table_patent.tsv', Patent),
        (f'{base_path_data_tables}table_image_prepared.csv', Image),

        (f'{base_path_data_relations}patent_has_relations.tsv', PatentHasRelations),
        (f'{base_path_data_relations}patent_has_addresses.tsv', PatentHasAddresses),
        (f'{base_path_data_relations}person_has_addresses.tsv', PersonHasAddresses),
        (f'{base_path_data_relations}patent_has_images.tsv', PatentHasImages)
    ]

    for file_path, table_model in ORDER_IMPORT:
        load_tsv_to_db(file_path, table_model)
