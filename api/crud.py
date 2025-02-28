"""
crud.py

CRUD operations.
Reusable functions to interact with the data in the database.
"""
from typing import (Union,
                    List)


from sqlalchemy.orm import Session
from .models.models import User, Person, Patent, PersonHasAddresses


def get_user(db: Session, args: dict) \
        -> Union[User, None]:
    """Get a user from the database."""
    return db.query(User).filter_by(**args).first()

def get_printer(db: Session, args: dict) -> Union[Person, None]:
    """Get a printer from the database."""
    return db.query(Person).filter_by(**args).first()

def get_printer_personal_addresses(db: Session, args: dict) -> list:
    """Get a printer's personal addresses from the database."""
    pass

def get_patents(db: Session, args: dict) -> list:
    """Get patents from the database."""
    return db.query(Patent).filter_by(**args).all()
