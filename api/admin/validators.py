import re

from wtforms import ValidationError

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