"""
widgets.py

Widgets or custom fields for views.
"""

from wtforms import SelectField, StringField
from wtforms.widgets import TextArea
from wtforms import TextAreaField
from flask_admin.form.widgets import Select2Widget



class QuillWidget(TextAreaField):
    def __init__(self, *args, **kwargs):
        kwargs['render_kw'] = {'onready': 'createQuillEditor(this)'}
        super().__init__(*args, **kwargs)

