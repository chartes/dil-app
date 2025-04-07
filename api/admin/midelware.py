from flask import Flask, g, request
from api.database import session

def init_app(app: Flask):
    @app.teardown_appcontext
    def remove_session(exception=None):
        session.remove()
