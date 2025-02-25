"""
crud.py

CRUD operations.
Reusable functions to interact with the data in the database.
"""
from typing import (Union,
                    List)
from sqlalchemy.orm import Session
from .models.models import User

def get_user(db: Session, args: dict) \
        -> Union[User, None]:
    """Get a user from the database."""
    return db.query(User).filter_by(**args).first()