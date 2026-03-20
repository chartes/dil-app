# -*- coding: utf-8 -*-
"""
crud.py

CRUD operations.
Reusable functions to interact with the data in the database.
"""

from typing import Type, Union
import re

from sqlalchemy.orm import Session

import bleach


from .models.models import User, Person, Patent, City, Address, Image
from .models.constants import type_patent_relations
from api.api_utils import normalize_firstnames

MARKUP_HTML_FIELDS = {"personal_information", "professional_information"}
inverted_type_relations = {v: k for k, v in type_patent_relations.items()}


def get_user(db: Session, args: dict) -> Union[User, None]:
    """Get a user from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: The first User object that matches the filter criteria, or None if no match
                is found or if an exception occurs during the query.
    :rtype: User | None
    """
    try:
        return db.query(User).filter_by(**args).first()
    except Exception:
        return None


def clean_html_markup(html_markup: str) -> Union[str, None]:
    """Clean HTML markup from a string, allowing only <br> tags and stripping all others.

    :param html_markup: The input string containing HTML markup to clean.
    :type html_markup: str
    :return: A cleaned string with only <br> tags preserved, or None if the input is None.
    :rtype: str | None
    """
    if html_markup:
        return bleach.clean(re.sub(r"<br>", " <br>", html_markup), strip=True, tags=[])
    else:
        return None


def enhance_patent_response(
    db: Session, patent: Type[Patent], html_markup: bool = False
) -> dict:
    """Enhance patent response.

    :param db: The database session to use for the query.
    :type db: Session
    :param patent: The Patent object to enhance.
    :type patent: Type[Patent]
    :param html_markup: A boolean indicating whether to preserve HTML markup in the references field.
    :type html_markup: bool
    :return: A dictionary containing the enhanced patent information, including cleaned references and related entities.
    :rtype: dict
    """
    return {
        "_id_dil": str(patent._id_dil) if patent._id_dil else None,
        "city_label": patent.city_label,
        "city_id": str(get_city(db, {"id": patent.__dict__["city_id"]})._id_dil)
        if patent.__dict__["city_id"]
        else None,
        "date_start": patent.date_start,
        "date_end": patent.date_end,
        "references": clean_html_markup(patent.references)
        if not html_markup
        else patent.references,
        "professional_addresses": [
            {
                "_id_dil": str(address.address_patents._id_dil)
                if address.address_patents._id_dil
                else None,
                "label": address.address_patents.label,
                "city_label": address.address_patents.city_label,
                "city_id": str(address.address_patents.city._id_dil)
                if address.address_patents.city_id
                else None,
                "date_occupation": address.date_occupation,
            }
            for address in patent.addresses_relations
            if len(patent.addresses_relations) > 0
        ],
        "patent_relations": [
            {
                "_id_dil": str(patent_relation.person_related._id_dil)
                if patent_relation.person_related._id_dil
                else None,
                "lastname": patent_relation.person_related.lastname,
                "firstnames": normalize_firstnames(
                    patent_relation.person_related.firstnames
                ),
                "type": inverted_type_relations.get(patent_relation.type),
            }
            for patent_relation in patent.patent_relations
            if len(patent.patent_relations) > 0
        ],
    }


def enhance_printer_response(
    db: Session, printer: Type[Person], html_markup: bool = False
) -> dict:
    """Enhance printer response with cleaner html.

    :param db: The database session to use for the query.
    :type db: Session
    :param printer: The Person object representing the printer to enhance.
    :type printer: Type[Person]
    :param html_markup: A boolean indicating whether to preserve HTML markup in the personal and professional
                        information fields.
    :type html_markup: bool
    :return: A dictionary containing the enhanced printer information, including cleaned personal and professional
                information, as well as related patents and addresses.
    :rtype: dict
    """
    if not html_markup:
        for field in MARKUP_HTML_FIELDS:
            value = printer.__dict__[field]
            converted = "" if value is None else str(value)
            if isinstance(converted, str):
                printer.__dict__[field] = clean_html_markup(converted)

    return {
        "_id_dil": str(printer._id_dil) if printer._id_dil else None,
        "lastname": printer.lastname,
        "firstnames": normalize_firstnames(printer.firstnames),
        "birth_date": printer.birth_date,
        "birth_city_label": printer.birth_city_label,
        "birth_city_id": str(
            get_city(db, {"id": printer.__dict__["birth_city_id"]})._id_dil
        )
        if printer.__dict__["birth_city_id"]
        else None,
        "personal_information": printer.personal_information,
        "professional_information": printer.professional_information,
        "personal_addresses": [
            {
                "_id_dil": str(address.address_persons._id_dil)
                if address.address_persons._id_dil
                else None,
                "label": address.address_persons.label,
                "city_label": address.address_persons.city_label,
                "city_id": str(address.address_persons.city._id_dil)
                if address.address_persons.city_id
                else None,
                "date_occupation": address.date_occupation,
            }
            for address in printer.addresses_relations
            if len(printer.addresses_relations) > 0
        ],
        "patents": [
            enhance_patent_response(db, patent, html_markup=html_markup)
            for patent in printer.patents
            if len(printer.patents) > 0
        ],
    }


def get_printer(
    db: Session, args: dict, enhance: bool = False
) -> Union[dict, Type[Person], None]:
    """Get a printer from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :param enhance: A boolean indicating whether to enhance the printer response with cleaner HTML and related
                    entities.
    :type enhance: bool
    :return: A dictionary containing the enhanced printer information if enhance is True, the Person object
                if enhance is False, or None if no matching printer is found.
    :rtype: dict | Type[Person] | None
    """
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
    """Get persons from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :param enhance: A boolean indicating whether to enhance the printer responses with cleaner HTML and related
                    entities.
    :type enhance: bool
    :return: A list of dictionaries containing the enhanced printer information if enhance is True, or
                a list of Person objects if enhance is False. Returns an empty list if no matching printers are found.
    :rtype: list
    """
    printers = db.query(Person).filter_by(**args).all()
    if len(printers) > 0:
        if enhance:
            res = [
                {
                    "_id_dil": str(printer._id_dil) if printer._id_dil else None,
                    "lastname": printer.lastname,
                    "firstnames": normalize_firstnames(printer.firstnames),
                    "total_patents": len(printer.patents),
                }
                for printer in printers
            ]
            return res
        else:
            return printers
    else:
        return []


def get_patent(
    db: Session, args: dict, enhance: bool = False
) -> Union[dict, Type[Patent], None]:
    """Get a patent.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :param enhance: A boolean indicating whether to enhance the patent response with cleaner HTML and related
                    entities.
    :type enhance: bool
    :return: A dictionary containing the enhanced patent information if enhance is True, the Patent object
                if enhance is False, or None if no matching patent is found.
    :rtype: dict | Type[Patent] | None
    """
    html_markup = args.pop("html", False)
    patent = db.query(Patent).filter_by(**args).first()
    if patent:
        if enhance:
            return enhance_patent_response(db, patent, html_markup=html_markup)
        else:
            return patent
    else:
        return None


def get_cities(db: Session, args: dict) -> Union[list, None]:
    """Get cities from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: A list of City objects that match the filter criteria, or None if an
                exception occurs during the query.
    :rtype: list | None
    """
    try:
        return db.query(City).filter_by(**args).all()
    except Exception:
        return None


def get_addresses(db: Session, args: dict) -> Union[list, None]:
    """Get addresses from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: A list of Address objects that match the filter criteria, or None if an
                exception occurs during the query.
    :rtype: list | None
    """
    return db.query(Address).filter_by(**args).all()


def get_city(db: Session, args: dict) -> Union[City, None]:
    """Get a city

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: The first City object that matches the filter criteria, or None if no match
                is found or if an exception occurs during the query.
    :rtype: City | None
    """
    return db.query(City).filter_by(**args).first()


def get_address(db: Session, args: dict) -> Union[Address, None]:
    """Get an address.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: The first Address object that matches the filter criteria, or None if no match
                is found or if an exception occurs during the query.
    :rtype: Address | None
    """
    return db.query(Address).filter_by(**args).first()


def get_image(db: Session, args: dict) -> Union[Image, None]:
    """Get images from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: The first Image object that matches the filter criteria, or None if no match
                is found or if an exception occurs during the query.
    :rtype: Image | None
    """
    return db.query(Image).filter_by(**args).first()


def get_patents(db: Session, args: dict) -> list:
    """Get patents from the database.

    :param db: The database session to use for the query.
    :type db: Session
    :param args: A dictionary of filter arguments to apply to the query.
    :type args: dict
    :return: A list of Patent objects that match the filter criteria.
    :rtype: list
    """
    return db.query(Patent).filter_by(**args).all()
