"""
schemas.py

Pydantic models for API endpoints.
Use for validation and serialization.
"""

from typing import Union, List, Optional
from pydantic import BaseModel, Field

class BaseMeta(BaseModel):
    """An abstract base class for meta schemas."""
    id_dil: str = Field(..., alias="_id_dil")

    class Config:
        orm_mode = True

class Message(BaseModel):
    message: str = Field(alias="message")

class CityOut(BaseMeta):
    label: Optional[str] = Field(..., alias="label")
    country_iso_code: Optional[str] = Field(..., alias="country_iso_code")
    long_lat: Optional[str] = Field(..., alias="long_lat")
    insee_fr_code: Optional[str] = Field(..., alias="insee_fr_code")
    insee_fr_department_code: Optional[str] = Field(..., alias="insee_fr_department_code")
    insee_fr_department_label: Optional[str] = Field(..., alias="insee_fr_department_label")
    geoname_id: Optional[str] = Field(..., alias="geoname_id")
    wikidata_item_id: Optional[str] = Field(..., alias="wikidata_item_id")
    dicotopo_item_id: Optional[str] = Field(..., alias="dicotopo_item_id")
    databnf_ark: Optional[str] = Field(..., alias="databnf_ark")
    viaf_id: Optional[str] = Field(..., alias="viaf_id")
    siaf_id: Optional[str] = Field(..., alias="siaf_id")

class CityOutMinimal(BaseModel):
    label: Optional[str] = Field(..., alias="label")


class AddressOut(BaseMeta):
    label: Optional[str] = Field(..., alias="label")
    city_label: Optional[str]  = Field(..., alias="city_label")
    city_id: Optional[int]  = Field(..., alias="city_id")

class AddressMinimalOut(BaseMeta):
    label: Optional[str] = Field(..., alias="label")
    city_label: Optional[str]  = Field(..., alias="city_label")
    city_id: Optional[str]  = Field(..., alias="city_id")

class AddressPersonalOut(AddressMinimalOut):
    date_occupation: Optional[str] = Field(..., alias="date_occupation")


class PrinterRelationOut(BaseMeta):
    lastname: Optional[str]
    firstnames: Optional[str]
    type: Optional[str]

class PatentMinimalOut(BaseMeta):
    city_label: Optional[str]
    date_start: Optional[str]
    date_end: Optional[str]

class PatentOut(BaseMeta):
    """Schema with minimal information on a patent."""
    city_label: Optional[str]
    city_id: Optional[str]
    date_start: Optional[str]
    date_end: Optional[str]
    references: Optional[str]
    professional_addresses: Union[List[AddressMinimalOut], None]
    patent_relations: Union[List[PrinterRelationOut], None]

class PrinterMinimalOut(BaseMeta):
    lastname: str
    firstnames: Optional[str]

class PrinterMinimalResponseOut(PrinterMinimalOut):
    total_patents: Optional[int] = 0
    highlight: Optional[str] = None


class PrinterOut(PrinterMinimalOut):
    birth_date: Optional[str]
    birth_city_label: Optional[str]
    birth_city_id: Optional[str]
    personal_information: Optional[str]
    professional_information: Optional[str]
    addresses_relations: Union[List[AddressPersonalOut], None] = Field(..., alias="personal_addresses")
    patents: Union[List[PatentOut], None]

class ImageOut(BaseModel):
    image_id: Optional[str]
    label: Optional[str]
    reference_url: Optional[str]
    img_name: Optional[str]
    iiif_url: Optional[str]
    is_pinned: Optional[bool]

class PatentImages(BaseModel):
    patent_id: Optional[str]
    images: List[ImageOut]

class PersonPatentsImages(BaseModel):
    person_id: Optional[str]
    patent_images: List[PatentImages]
    images_pinned: List[ImageOut]
    total_images: Optional[int]
    total_images_pinned: Optional[int]
