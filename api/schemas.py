"""
schemas.py

Pydantic models for API endpoints.
Use for validation and serialization.
"""

from typing import Union, List, Optional
from pydantic import BaseModel, Field

class BaseMeta(BaseModel):
    """An abstract base class for meta schemas."""
    id_dil: str = Field(alias="_id_dil")

    class Config:
        from_attributes = True
        populate_by_name = True

class AddressOut(BaseMeta):
    """Schema with minimal information on an address."""
    id: int
    label: str
    city_label: str


class PatentOut(BaseMeta):
    """Schema with minimal information on a patent."""
    id: int
    city_label: Optional[str]
    date_start: Optional[str]


class PrinterOut(BaseMeta):
    """Schema with minimal information on a printer."""
    # id: int
    lastname: str
    firstnames: str
    birth_date: Optional[str]
    birth_city_label: Optional[str]
    personal_information: Optional[str]
    professional_information: Optional[str]
    addresses_relations: Union[List[AddressOut], None]
    patents: Union[List[PatentOut], None]


class Message(BaseModel):
    """Schema for generic messages."""
    message: str = Field(alias="message")