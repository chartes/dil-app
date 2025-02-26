"""
config.py

Settings for the application.
By default, the application will run in debug mode.
[prod | dev] only. go to tests/ for testing settings.
"""
import dotenv

import os
import pathlib

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, BaseModel

# Set the base directory for the project
BASE_DIR = pathlib.Path(__file__).parent.parent

# Load the environment variables (by, default, the dev environment)
mode = os.environ.get("ENV", "dev")
env_file = BASE_DIR / f".{mode}.env"
print(env_file)
dotenv.load_dotenv(env_file)

class Settings(BaseSettings):
    # ~ General settings ~
    DEBUG: bool = bool(os.environ.get("DEBUG", True))
    PORT: int = int(os.environ.get("PORT", 8000))
    HOST: str = str(os.environ.get("HOST", "127.0.0.1"))
    TESTING: bool = bool(os.environ.get("TESTING", False))
    WORKERS: int = int(os.environ.get("WORKERS", 2))

    # ~ Flask settings (admin part) ~
    FLASK_SECRET_KEY: str = str(os.environ.get("FLASK_SECRET_KEY", ""))
    FLASK_BABEL_DEFAULT_LOCALE: str = str(os.environ.get("FLASK_BABEL_DEFAULT_LOCALE", "fr"))

    FLASK_MAIL_SERVER: str = str(os.environ.get("FLASK_MAIL_SERVER", ""))
    FLASK_MAIL_PORT: int = int(os.environ.get("FLASK_MAIL_PORT", 587))
    FLASK_MAIL_USE_TLS: bool = bool(os.environ.get("FLASK_MAIL_USE_TLS", True))
    FLASK_MAIL_USE_SSL: bool = bool(os.environ.get("FLASK_MAIL_USE_SSL", False))
    FLASK_MAIL_USERNAME: str = str(os.environ.get("FLASK_MAIL_USERNAME", ""))
    FLASK_MAIL_PASSWORD: str = str(os.environ.get("FLASK_MAIL_PASSWORD", ""))

    FLASK_ADMIN_NAME: str = str(os.environ.get("FLASK_ADMIN_NAME", "admin"))
    FLASK_ADMIN_MAIL: str = str(os.environ.get("FLASK_ADMIN_MAIL", ""))
    FLASK_ADMIN_ADMIN_PASSWORD: str = str(os.environ.get("FLASK_ADMIN_ADMIN_PASSWORD", ""))

    # ~ PWD Generation settings ~
    PWD_LENGTH: str = str(os.environ.get("PWD_LENGTH", "8,16"))
    PWD_PREFIX: str = str(os.environ.get("PWD_PREFIX", "fa-"))
    PWD_SUFFIX: str = str(os.environ.get("PWD_SUFFIX", "!,?"))

    # ~ Database settings ~
    DB_URI: str = str(os.environ.get("DB_URI", "db/DIL.db"))
    DB_ECHO: bool = bool(os.environ.get("DB_ECHO", False))

    # ~ Index settings ~
    WHOOSH_INDEX_DIR: str = str(os.environ.get("WHOOSH_INDEX_DIR", "index_dil"))

    # ~ Image settings ~
    IMAGE_STORE: str = str(os.environ.get("IMAGE_STORE", "static/images_store"))

    # Class configuration
    model_config = ConfigDict(env_file=env_file,
                              env_file_encoding="utf-8")
    #class Config:
    #    env_file = env_file
    #    env_file_encoding = "utf-8"

settings = Settings()