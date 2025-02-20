import re
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

def is_only_digits(_, field):
    """Validate that the field contains only digits."""
    value = str(field.data)
    if not value.isdigit():
        raise ValidationError("Ce champ ne peut contenir que des chiffres.")

def is_wikidata_qid(_, field):
    """Validate that the value is a valid Wikidata QID."""
    value = str(field.data)
    pattern = r"^(Q\d+)$"
    match = bool(re.match(pattern, value))
    if not match:
        raise ValidationError("Le format de l'identifiant Wikidata est incorrect.")

def is_ark_id(_, field):
    """Validate that the value is a valid ARK identifier."""
    value = str(field.data)
    pattern = r"^(ark:\/[A-Za-z0-9]{5,9}\/\w+)$"
    match = bool(re.match(pattern, value))
    if not match:
        raise ValidationError("Le format de l'identifiant ARK est incorrect. Attention : inclure le préfixe 'ark:/'. "
                              "Ex. ark:/12148/bpt6k1041293j")

def validate_coordinates(_, field):
    """Validate that the value is a valid longitude/latitude pair.
    Format example: (-0.57918, 44.837789)"""
    value = str(field.data)
    pattern = r"^\(\s*(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)\s*\)$"
    match = re.match(pattern, value)
    if not match:
        raise ValidationError("Le format de la longitude/latitude est incorrect. Ex. (-0.57918, 44.837789) ou (60.4, -20.3522)")


def validate_address(form, field):
    """Validate that the value is a valid address."""
    # get from form checkbox value
    is_not_french = bool(form.data['not_french_address'])
    if not is_not_french:
        value = str(field.data)
        pattern = r"^(inconnue|(?:\d{1,10}(?:\s*(?:bis|ter|quater|quinquies))?,\s)?[^\d].+)$"
        match = re.match(pattern, value, re.IGNORECASE)

        if not match:
            raise ValidationError("Format d'adresse invalide. Exemples d'adresses valides : '1, rue de la Paix', 'inconnue', '2 bis, rue du Faubourg Saint-Honoré', 'rue de la Paix', '12 quinquies, rue Victor Hugo', '3 ter, avenue des Champs-Élysées' etc.")

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
                    "Ex. http://www.example.com ou https://example.com ou https://example.com")

def is_circular_person_patent_relation(person_id, person_related_id, type_relation, patent_id):
    """Validate that the person and patent are not related to the same person."""
    if person_id == person_related_id:
        # find key in type_patent_relations dictionary
        type_relation = [k for k, v in type_patent_relations.items() if v == type_relation][0]
        raise ValidationError(f"Une relation de type '{type_relation}' ne peut pas être créée entre une personne et "
                              f"elle-même (ID={person_id}) pour le brevet ID={patent_id}. Veuillez corriger la relation "
                              f"avant d'enregistrer de nouveau.")
