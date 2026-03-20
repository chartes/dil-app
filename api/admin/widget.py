# -*- coding: utf-8 -*-

"""
widgets.py

Widgets or custom fields for views.
"""

from wtforms import TextAreaField


class QuillWidget(TextAreaField):
    """Custom widget for a rich text editor using Quill.js in the admin interface."""

    def __init__(self, *args, **kwargs):
        kwargs["render_kw"] = {"onready": "createQuillEditor(this)"}
        super().__init__(*args, **kwargs)
