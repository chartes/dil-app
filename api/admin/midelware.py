# -*- coding: utf-8 -*-
"""midelware.py

Middleware for the admin interface, including teardown functions to remove database sessions after each request.
"""

from flask import Flask
from api.database import session


def init_app(app: Flask) -> None:
    """Initialize the Flask app with middleware for the admin interface.

    :param app: The Flask application instance to initialize.
    :type app: Flask
    """

    @app.teardown_appcontext
    def remove_session(exception=None):
        session.remove()
