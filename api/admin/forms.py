from wtforms import Form, StringField, SelectField, IntegerField, validators


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