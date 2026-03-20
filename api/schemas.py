# -*- coding: utf-8 -*-
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
        allow_population_by_field_name = True


class Message(BaseModel):
    """Schema for a simple message response."""

    message: str = Field(alias="message")


class CityOut(BaseMeta):
    """Schema for city information."""

    label: Optional[str] = Field(..., alias="label")
    country_iso_code: Optional[str] = Field(..., alias="country_iso_code")
    long_lat: Optional[str] = Field(..., alias="long_lat")
    insee_fr_code: Optional[str] = Field(..., alias="insee_fr_code")
    insee_fr_department_code: Optional[str] = Field(
        ..., alias="insee_fr_department_code"
    )
    insee_fr_department_label: Optional[str] = Field(
        ..., alias="insee_fr_department_label"
    )
    geoname_id: Optional[str] = Field(..., alias="geoname_id")
    wikidata_item_id: Optional[str] = Field(..., alias="wikidata_item_id")
    dicotopo_item_id: Optional[str] = Field(..., alias="dicotopo_item_id")
    databnf_ark: Optional[str] = Field(..., alias="databnf_ark")
    viaf_id: Optional[str] = Field(..., alias="viaf_id")
    siaf_id: Optional[str] = Field(..., alias="siaf_id")


class CityOutMinimal(BaseModel):
    """Schema for minimal city information."""

    id: Optional[str] = Field(..., alias="id")
    id_dil: Optional[str] = Field(..., alias="id_dil")
    label: Optional[str] = Field(..., alias="label")
    department_label_fr: Optional[str] = Field(..., alias="department_label_fr")
    total_persons_if_selected: Optional[int] = Field(
        ..., alias="total_persons_if_selected"
    )
    total_patents_if_selected: Optional[int] = Field(
        ..., alias="total_patents_if_selected"
    )


class AddressOut(BaseMeta):
    """Schema for address information."""

    label: Optional[str] = Field(..., alias="label")
    city_label: Optional[str] = Field(..., alias="city_label")
    city_id: Optional[int] = Field(..., alias="city_id")


class AddressMinimalOut(BaseMeta):
    """Schema for minimal address information."""

    label: Optional[str] = Field(..., alias="label")
    city_label: Optional[str] = Field(..., alias="city_label")
    date_occupation: Optional[str] = Field(..., alias="date_occupation")
    city_id: Optional[str] = Field(..., alias="city_id")


class AddressPersonalOut(AddressMinimalOut):
    """Schema for personal address information."""

    date_occupation: Optional[str] = Field(..., alias="date_occupation")


class PrinterRelationOut(BaseMeta):
    """Schema for printer relation information."""

    lastname: Optional[str]
    firstnames: Optional[str]
    type: Optional[str]


class PatentMinimalOut(BaseMeta):
    """Schema with minimal information on a patent."""

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
    """Schema with minimal information on a printer."""

    lastname: str
    firstnames: Optional[str]


class ExercisePlaceSummaryOut(BaseModel):
    """Schema for summarizing exercise places."""

    city_label: str
    date_start: Optional[str] = None
    date_end: Optional[str] = None


class PrinterMinimalResponseOut(PrinterMinimalOut):
    """Schema for printer response with minimal information and additional details."""

    person_pk: Optional[int] = None
    total_patents: Optional[int] = 0
    highlight_text: Optional[str] = None
    highlight: Optional[str] = None
    exercise_places_summary: List[ExercisePlaceSummaryOut] = []


class PrinterOut(PrinterMinimalOut):
    """Schema with detailed information on a printer."""

    birth_date: Optional[str]
    birth_city_label: Optional[str]
    birth_city_id: Optional[str]
    personal_information: Optional[str]
    professional_information: Optional[str]
    addresses_relations: Union[List[AddressPersonalOut], None] = Field(
        ..., alias="personal_addresses"
    )
    patents: Union[List[PatentOut], None]


class ImageOut(BaseModel):
    """Schema for image information."""

    image_id: Optional[str]
    label: Optional[str]
    reference_url: Optional[str]
    img_name: Optional[str]
    iiif_url: Optional[str]
    is_pinned: Optional[bool]


class PatentImages(BaseModel):
    """Schema for patent images information."""

    patent_id: Optional[str]
    images: List[ImageOut]


class PersonPatentsImages(BaseModel):
    """Schema for summarizing a person's patents and their associated images."""

    person_id: Optional[str]
    patent_images: List[PatentImages]
    images_pinned: List[ImageOut]
    total_images: Optional[int]
    total_images_pinned: Optional[int]
