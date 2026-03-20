# -*- coding: utf-8 -*-

"""validators.py

Custom validators for the admin interface, including date format validation, URL validation, and relationship validation between people and patents.
"""

import re
from wtforms import ValidationError
from api.models.constants import type_patent_relations


def is_custom_date_format(value: str) -> bool:
    """Validate that the date is in the correct format.

    Accepted formats:
    - AAAA-MM-JJ
    - AAAA-MM
    - AAAA
    - ~AAAA
    - ~AAAA-MM
    - ~AAAA-MM-JJ
        (the prefix '~' indicates an approximate date).

    :param value: The date string to validate.
    :type value: str
    :return: True if the date is in a valid format, False otherwise.
    :rtype: bool
    """
    pattern = r"^(?:~?\d{4}(?:-(?:0[1-9]|1[0-2])(?:-(?:0[1-9]|1\d|2\d|3[01]))?)?)$"
    return bool(re.match(pattern, value))


def is_valid_date_format(field: object, add_text: str = "") -> None:
    """Validate that the date is in the correct format.

    Accepted formats:
    - AAAA-MM-JJ
    - AAAA-MM
    - AAAA
    - ~AAAA
    - ~AAAA-MM
    - ~AAAA-MM-JJ
        (the prefix '~' indicates an approximate date).

    :param field: The form field containing the date string to validate.
    :type field: object
    :param add_text: Additional text to include in the error message if validation fails.
    :type add_text: str
    :raises ValidationError: If the date format is incorrect.

    """
    if not is_custom_date_format(str(field)):
        raise ValidationError(
            "Le format de la date est incorrect."
            " Veuillez utiliser les formats suivants : AAAA-MM-JJ ou AAAA-MM ou AAAA ou"
            " ~AAAA ou ~AAAA-MM ou ~AAAA-MM-JJ (le préfixe '~' désigne une date approximative)."
            f" {add_text}"
        )


def is_valid_date(_, field: object) -> None:
    """validate that the date is in the correct format.
    Use this for views exclusively.

    :param _: Unused parameter for compatibility with WTForms validators.
    :type _: object
    :param field: The form field containing the date string to validate.
    :type field: object
    :raises ValidationError: If the date format is incorrect.
    """
    is_valid_date_format(field.data)


def is_only_digits(_, field: object) -> None:
    """Validate that the field contains only digits.

    :param _: Unused parameter for compatibility with WTForms validators.
    :type _: object
    :param field: The form field to validate.
    :type field: object
    :raises ValidationError: If the field contains characters other than digits.
    """
    value = str(field.data)
    if not value.isdigit():
        raise ValidationError("Ce champ ne peut contenir que des chiffres.")


def is_wikidata_qid(_, field: object) -> None:
    """Validate that the value is a valid Wikidata QID.

    :param _: Unused parameter for compatibility with WTForms validators.
    :type _: object
    :param field: The form field containing the Wikidata QID to validate.
    :type field: object
    :raises ValidationError: If the Wikidata QID format is incorrect.
    """
    value = str(field.data)
    pattern = r"^(Q\d+)$"
    match = bool(re.match(pattern, value))
    if not match:
        raise ValidationError("Le format de l'identifiant Wikidata est incorrect.")


def is_ark_id(_, field: object) -> None:
    """Validate that the value is a valid ARK identifier.

    :param _: Unused parameter for compatibility with WTForms validators.
    :type _: object
    :param field: The form field containing the ARK identifier to validate.
    :type field: object
    :raises ValidationError: If the ARK identifier format is incorrect.
    """
    value = str(field.data)
    pattern = r"^(ark:\/[A-Za-z0-9]{5,9}\/\w+)$"
    match = bool(re.match(pattern, value))
    if not match:
        raise ValidationError(
            "Le format de l'identifiant ARK est incorrect. Attention : inclure le préfixe 'ark:/'. "
            "Ex. ark:/12148/bpt6k1041293j"
        )


def validate_coordinates(_, field: object) -> None:
    """Validate that the value is a valid longitude/latitude pair.
    Format example: (-0.57918, 44.837789).

    :param _: Unused parameter for compatibility with WTForms validators.
    :type _: object
    :param field: The form field containing the coordinates to validate.
    :type field: object
    :raises ValidationError: If the coordinates format is incorrect.
    """
    value = str(field.data)
    pattern = r"^\(\s*(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)\s*\)$"
    match = re.match(pattern, value)
    if not match:
        raise ValidationError(
            "Le format de la longitude/latitude est incorrect. Ex. (-0.57918, 44.837789) ou (60.4, -20.3522)"
        )


def validate_address(form: object, field: object) -> None:
    """Validate that the value is a valid address.

        Accepted formats:
    - 'inconnue'
    - '1, rue de la Paix'
    - 'rue de la Paix'
    - '2 bis, rue du Faubourg Saint-Honoré'
    - '12 quinquies, rue Victor Hugo'
    - '3 ter, avenue des Champs-Élysées'

    :param form: The form containing the field to validate, used to access other form data if needed.
    :type form: object
    :param field: The form field containing the address to validate.
    :type field: object
    :raises ValidationError: If the address format is incorrect.
    """
    # get from form checkbox value
    is_not_french = bool(form.data["not_french_address"])
    if not is_not_french:
        value = str(field.data)
        pattern = (
            r"^(inconnue|(?:\d{1,10}(?:\s*(?:bis|ter|quater|quinquies))?,\s)?[^\d].+)$"
        )
        match = re.match(pattern, value, re.IGNORECASE)

        if not match:
            raise ValidationError(
                "Format d'adresse invalide. Exemples d'adresses valides : '1, rue de la Paix', 'inconnue', '2 bis, rue du Faubourg Saint-Honoré', 'rue de la Paix', '12 quinquies, rue Victor Hugo', '3 ter, avenue des Champs-Élysées' etc."
            )


def is_valid_url(_, field: object) -> None:
    """Validate that the URL is in the correct format.

    Accepted formats:
    - 'unknown_url'
    - 'http://www.example.com'
    - 'https://example.com'
    :param _: Unused parameter for compatibility with WTForms validators.
    :type _: object
    :param field: The form field containing the URL to validate.
    :type field: object
    :raises ValidationError: If the URL format is incorrect.
    """
    data = str(field.data)
    if data:
        if data != "unknown_url":
            pattern = r"^(https?).*$"
            match = bool(re.match(pattern, data))
            if not match:
                raise ValidationError(
                    "Le format de l'URL est incorrect. Veuillez inclure le protocole (http:// ou https://). "
                    "Ex. http://www.example.com ou https://example.com ou https://example.com"
                )


def is_circular_person_patent_relation(
    person_id: int, person_related_id: int, type_relation: str, patent_id: int
):
    """Validate that the person and patent are not related to the same person.

    :param person_id: The ID of the person in the relationship.
    :type person_id: int
    :param person_related_id: The ID of the related person in the relationship.
    :type person_related_id: int
    :param type_relation: The type of relationship between the person and the patent.
    :type type_relation: str
    :param patent_id: The ID of the patent involved in the relationship.
    :type patent_id: int
    :raises ValidationError: If the person is related to themselves for the given patent and relationship
    """
    if person_id == person_related_id:
        # find key in type_patent_relations dictionary
        type_relation = [
            k for k, v in type_patent_relations.items() if v == type_relation
        ][0]
        raise ValidationError(
            f"Une relation de type '{type_relation}' ne peut pas être créée entre une personne et "
            f"elle-même (ID={person_id}) pour le brevet ID={patent_id}. Veuillez corriger la relation "
            f"avant d'enregistrer de nouveau."
        )
