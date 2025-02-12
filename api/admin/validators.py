import re
import requests
from flask import url_for
from wtforms import ValidationError
from api.models.constants import type_patent_relations



def is_custom_date_format(value):
    pattern = r"^(?:~?\d{4}(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|1\d|2\d|3[01]))?)?)$"
    return bool(re.match(pattern, value))


def is_valid_date(_, field):
    """validate that the date is in the correct format"""
    if not is_custom_date_format(str(field.data)):
        raise ValidationError(
            "Le format de la date est incorrect."
            " Veuillez utiliser les formats suivants : AAAA-MM-JJ ou AAAA-MM ou AAAA ou"
            " ~AAAA ou ~AAAA-MM ou ~AAAA-MM-JJ (le préfixe '~' désigne une date approximative)"
        )


def is_valid_url(_, field):
    """Validate that the URL is in the correct format."""
    data = str(field.data)
    if data:
        if data != "unknown_url":
            pattern = r"^(https?).*$"
            match = bool(re.match(pattern, data))
            if not match:
                raise ValidationError(
                    "Le format de l'URL est incorrect. Veuillez inclure le protocole (http:// ou https://). "
                    "ex. http://www.example.com ou https://example.com ou https://example.com")

def is_circular_person_patent_relation(person_id, person_related_id, type_relation, patent_id):
    """Validate that the person and patent are not related to the same person."""
    if person_id == person_related_id:
        # find key in type_patent_relations dictionary
        type_relation = [k for k, v in type_patent_relations.items() if v == type_relation][0]
        raise ValidationError(f"Une relation de type '{type_relation}' ne peut pas être créée entre une personne et "
                              f"elle-même (ID={person_id}) pour le brevet ID={patent_id}. Veuillez corriger la relation "
                              f"avant d'enregistrer de nouveau.")
