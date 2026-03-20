# -*- coding: utf-8 -*-
"""forms.py

Forms for the admin interface, including a custom form for child relationships and a login form.
"""

from flask_wtf import FlaskForm
from wtforms import (
    Form,
    StringField,
    SelectField,
    IntegerField,
    PasswordField,
    BooleanField,
    SubmitField,
    validators,
)
from wtforms.validators import DataRequired


class CustomChildForm(Form):
    """Custom form for managing child relationships between people in the admin interface."""

    person_id = IntegerField("ID Personne", [validators.DataRequired()])
    person_related_id = IntegerField("ID Personne liée", [validators.DataRequired()])
    type = SelectField(
        "Type de relation",
        choices=[
            ("associé", "Associé"),
            ("parrain", "Parrain"),
            ("successeur", "Successeur"),
            ("prédécesseur", "Prédécesseur"),
        ],
        validators=[validators.DataRequired()],
    )


class LoginForm(FlaskForm):
    """Form for user login in the admin interface."""

    username = StringField("Utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")
