"""
widgets.py

Widgets or custom fields for views.
"""


from wtforms import TextAreaField


class QuillWidget(TextAreaField):
    def __init__(self, *args, **kwargs):
        kwargs['render_kw'] = {'onready': 'createQuillEditor(this)'}
        super().__init__(*args, **kwargs)
