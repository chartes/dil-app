from flask_wtf import FlaskForm
from wtforms import (Form,
                     StringField,
                     SelectField,
                     IntegerField,
                     PasswordField,
                     BooleanField,
                     SubmitField,
                     validators)
from wtforms.validators import DataRequired, Email, EqualTo

class CustomChildForm(Form):
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
    username = StringField('Utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')