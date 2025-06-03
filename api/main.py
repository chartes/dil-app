"""
main.py

Entry point for FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from api.admin import flask_app
from api.routes import api_router

from api.api_meta import METADATA


def create_app():
    """Create FastAPI application.
        :return: FastAPI application
        :rtype: FastAPI
        """
    # TODO: add to settings
    _app = FastAPI(
        title=METADATA["title"],
        description=METADATA["description"],
        version=METADATA["version"],
        openapi_url=METADATA["openapi_url"],
        docs_url=METADATA["docs_url"],
        redoc_url=METADATA["redoc_url"],
        license_info=METADATA["license_info"],
        swagger_ui_parameters=METADATA["swagger_ui_parameters"],
        openapi_tags=METADATA["openapi_tags"],
    )
    origins = [
        "*",
        "http://localhost",
        "http://localhost:8888",
        "http://localhost:9091",
        "http://localhost:9090",
    ]
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # extensions
    add_pagination(_app)
    # Add routes
    _app.include_router(api_router, prefix="/dil-db/api")
    # Mount admin interface (flask app) into FastAPI app
    # use threaded=True to avoid blocking the event loop
    _app.mount('/dil-db/', WSGIMiddleware(flask_app))
    return _app


app = create_app()