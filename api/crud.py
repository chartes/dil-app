"""
crud.py

CRUD operations.
Reusable functions to interact with the data in the database.
"""
from typing import (Union,
                    Type,
                    Any)
import re

from sqlalchemy.orm import (Session,
                            declared_attr)

import bleach


from .models.models import (User,
                            Person,
                            Patent,
                            City,
                            Address,
                            Image)
from .models.constants import type_patent_relations

MARKUP_HTML_FIELDS = {'personal_information', 'professional_information'}
inverted_type_relations = {v: k for k, v in type_patent_relations.items()}


def get_user(db: Session, args: dict) \
        -> Union[User, None]:
    """Get a user from the database."""
    return db.query(User).filter_by(**args).first()


def clean_html_markup(html_markup: str) -> str:
    if html_markup:
        return bleach.clean(
        re.sub(r"<br>",
               " <br>",
               html_markup),
        strip=True,
        tags=[]
    )
    else:
        return None

def enhance_patent_response(db: Session,
                            patent: Type[Patent],
                            html_markup: bool = False) -> dict:
    """Enhance patent response."""
    return {
                '_id_dil': str(patent._id_dil) if patent._id_dil else None,
                'city_label': patent.city_label,
                'city_id': str(get_city(db, {
                    "id": patent.__dict__["city_id"]})._id_dil) if patent.__dict__["city_id"] else None,
                'date_start': patent.date_start,
                'date_end': patent.date_end,
                'references': clean_html_markup(patent.references) if not html_markup else patent.references,
                'professional_addresses': [
                    {
                        '_id_dil': str(address.address_patents._id_dil) if address.address_patents._id_dil else None,
                        'label': address.address_patents.label,
                        'city_label': address.address_patents.city_label,
                        'city_id': str(address.address_patents.city._id_dil) if address.address_patents.city_id else None,
                        'date_occupation': address.date_occupation,
                    } for address in patent.addresses_relations
                if len(patent.addresses_relations) > 0],
                'patent_relations': [{
                    '_id_dil': str(patent_relation.person_related._id_dil) if patent_relation.person_related._id_dil else None,
                    'lastname': patent_relation.person_related.lastname,
                    'firstnames': patent_relation.person_related.firstnames,
                    'type': inverted_type_relations.get(patent_relation.type)

                } for patent_relation in patent.patent_relations if len(patent.patent_relations) > 0]
            }


def enhance_printer_response(db: Session,
                             printer: Type[Person],
                             html_markup) -> dict:
    """Enhance printer response with cleaner html."""
    if not html_markup:
        for field in MARKUP_HTML_FIELDS:
            value = printer.__dict__[field]
            converted = "" if value is None else str(value)
            if isinstance(converted, str):
                printer.__dict__[field] = clean_html_markup(converted)

    return {
        "_id_dil": str(printer._id_dil) if printer._id_dil else None,
        "lastname": printer.lastname,
        "firstnames": printer.firstnames,
        "birth_date": printer.birth_date,
        "birth_city_label": printer.birth_city_label,
        "birth_city_id": str(get_city(db, {
            "id": printer.__dict__["birth_city_id"]})._id_dil) if printer.__dict__["birth_city_id"] else None,
        "personal_information": printer.personal_information,
        "professional_information": printer.professional_information,
        "addresses_relations": [
            {
                '_id_dil': str(address.address_persons._id_dil) if address.address_persons._id_dil else None,
                'label': address.address_persons.label,
                'city_label': address.address_persons.city_label,
                'city_id': str(address.address_persons.city._id_dil) if address.address_persons.city_id else None,
                'date_occupation': address.date_occupation,
            } for address in printer.addresses_relations if len(printer.addresses_relations) > 0
        ],
        "patents": [
            enhance_patent_response(db, patent, html_markup=html_markup)
            for patent in printer.patents if len(printer.patents) > 0
        ]
    }




def get_printer(db: Session, args: dict, enhance: bool = False) -> Union[dict, None]:
    """Get a printer from the database."""
    html_markup = args.pop("html", False)
    printer = db.query(Person).filter_by(**args).first()
    if printer:
        if enhance:
            return enhance_printer_response(db, printer, html_markup=html_markup)
        else:
            return printer
    else:
        return None


def get_printers(db: Session, args: dict, enhance: bool = False) -> list:
    """Get persons from the database."""
    printers = db.query(Person).filter_by(**args).all()
    if len(printers) > 0:
        if enhance:
            res = [
                {
                    "_id_dil": str(printer._id_dil) if printer._id_dil else None,
                    "lastname": printer.lastname,
                    "firstnames": printer.firstnames,
                    "total_patents": len(printer.patents),
                }
                for printer in printers
            ]
            return res
        else:
            return printers
    else:
        return []

def get_patent(db: Session, args: dict, enhance: bool = False) -> Union[dict, None]:
    """Get a patent"""
    html_markup = args.pop("html", False)
    patent = db.query(Patent).filter_by(**args).first()
    if patent:
        if enhance:
            return enhance_patent_response(db, patent, html_markup=html_markup)
        else:
            return patent
    else:
        return None

# TODO: refactor with this below :
"""
def get_entity(db: Session, model, args: dict):
    # Get an entity from the database.
    return db.query(model).filter_by(**args).first()

def get_entities(db: Session, model, args: dict):
    # Get entities from the database.
    return db.query(model).filter_by(**args).all()
"""

def get_cities(db: Session, args: dict) -> list[Type[City]]:
    """Get cities from the database."""
    return db.query(City).filter_by(**args).all()

def get_addresses(db: Session, args: dict) -> list[Type[Address]]:
    """Get addresses from the database."""
    return db.query(Address).filter_by(**args).all()

def get_city(db: Session, args: dict) -> Union[City, None]:
    """Get a city"""
    return db.query(City).filter_by(**args).first()

def get_address(db: Session, args: dict) -> Union[Address, None]:
    """Get an address"""
    return db.query(Address).filter_by(**args).first()


def get_printer_personal_addresses(db: Session, args: dict) -> list:
    """Get a printer's personal addresses from the database."""
    pass

def get_image(db: Session, args: dict) -> list:
    """Get images from the database."""
    return db.query(Image).filter_by(**args).first()

def get_patents(db: Session, args: dict) -> list:
    """Get patents from the database."""
    return db.query(Patent).filter_by(**args).all()
