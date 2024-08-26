"""
Modèle V1.1.1 de la base de données de DIL-App

Commentaires:
 - On part du modèle V1.1.0
 - On déporte la ville de travail de l'imprimeur dans une table à part (ce qui peut permettre le liage de la ville aux adresses plus tard)
"""


import enum
import datetime

from sqlalchemy import (Column,
                        DateTime,
                        Boolean,
                        ForeignKey,
                        Integer,
                        String,
                        UniqueConstraint,
                        Enum,
                        CheckConstraint,
                        Text)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

__version__ = "1.1.1"

Base = declarative_base()

# -- enumeration lists --
class BaseEnum(enum.Enum):
    @classmethod
    def get_enum_values(cls):
        return (item.value for item in cls)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class PrinterRelationLabels(BaseEnum):
    """Liste contrôlée des types de relations entre imprimeurs

    :param PARTNER: associé
    :param SPONSOR: parrain
    :param SUCCESSOR: successeur
    :param OTHER_PATENT: autre brevet
    """
    __order__ = "PARTNER SPONSOR SUCCESSOR OTHER_PATENT"
    PARTNER = "associé"
    SPONSOR = "parrain"
    SUCCESSOR = "successeur"
    OTHER_PATENT = "autre brevet"


class AdressTypeLabels(BaseEnum):
    """Liste contrôlée des types d'adresses

    :param PROFESSIONAL: adresse professionnelle
    :param PERSONAL: adresse personnelle
    """
    __order__ = "PROFESSIONAL PERSONAL"
    PROFESSIONAL = "professionnelle"
    PERSONAL = "personnelle"


# -- main tables --

class Adresses(Base):
    """Table principale des adresses
    """
    __tablename__ = "adresses"
    __prefix__ = "adress"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False, unique=False)
    adresses_type = Column(Enum(AdressTypeLabels), nullable=False, unique=False)
    adresses_content = Column(Text, nullable=True, unique=False)

    printer = relationship("Printer", back_populates="adresses")


class City(Base):
    """Table principale des villes
    """
    __tablename__ = "cities"
    __prefix__ = "city"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    name = Column(String(255), nullable=False, unique=False)
    department = Column(String(25), nullable=True, unique=False)
    # optionnel
    longitude = Column(String(25), nullable=True, unique=False)
    latitude = Column(String(25), nullable=True, unique=False)

    printers = relationship("Printer", back_populates="working_city")


class Printer(Base):
    """Table principale des imprimeurs
    """
    __tablename__ = "printers"
    __prefix__ = "printer"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    lastname = Column(String(255), nullable=False, unique=False)
    firstname = Column(String(255), nullable=False, unique=False)
    patent_date_start = Column(String(25), nullable=True, unique=False)
    patent_date_end = Column(String(25), nullable=True, unique=False)
    working_city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, unique=False)
    working_city = relationship("City", back_populates="printers")
    bibliography_sources = Column(Text, nullable=True, unique=False)
    comment = Column(Text, nullable=True, unique=False)

    images = relationship("Image",
                          foreign_keys="Image.printer_id",
                          cascade="all, delete-orphan",
                          lazy="dynamic",
                          back_populates="printer")

    addresses = relationship("Adresses",
                             back_populates="printer",
                             cascade="all, delete-orphan",
                             lazy="dynamic")

    printer_relations = relationship("PrinterHasRelationType",
                                     back_populates="related_printer",
                                     foreign_keys="PrinterHasRelationType.related_printer_id",
                                        cascade="all, delete-orphan")

    # informations dont on dispose sur l"imprimeur mais qui ne sont pas affichés (a voir...)
    date_of_birth = Column(String(25), nullable=True, unique=False)
    loc_of_birth = Column(String(255), nullable=True, unique=False)
    arrondissement = Column(String(25), nullable=True, unique=False)
    professional_cv = Column(Text, nullable=True, unique=False)

    _created_at = Column(DateTime(timezone=True), nullable=False, unique=False, default=datetime.datetime.now())
    _updated_at = Column(DateTime(timezone=True), nullable=False, unique=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    _last_editor = Column(String(45), nullable=False, unique=False)


class Image(Base):
    """Table principale des images associées aux imprimeurs
    """
    __tablename__ = "images"
    __prefix__ = "image"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False, unique=False)
    title = Column(String(255), nullable=False, unique=False)
    is_illustration = Column(Boolean, nullable=False, unique=False, default=False)
    reference_url_source = Column(String(255), nullable=True, unique=False)
    local_uri_path = Column(String(255), nullable=True, unique=False)

    """Contrainte a gérer dans un event listener type before update
    __table_args__ = (
        UniqueConstraint("printer_id", "is_illustration",
                         name="uq_printer_illustration",
                         condition=(is_illustration is True))
    )
    """

    printer = relationship("Printer", back_populates="images")

# -- relation tables --


class PrinterHasRelationType(Base):
    """Table de relations typées entre imprimeurs
    """
    __tablename__ = "printer_has_relation_type"
    __prefix__ = "printer_has_relation_type"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, unique=False)
    related_printer_id = Column(Integer, ForeignKey("printers.id", ondelete="CASCADE"), nullable=False, unique=False)
    relation_type = Column(Enum(PrinterRelationLabels), nullable=False, unique=False)

    __table_args__ = (
        CheckConstraint("printer_id != related_printer_id", name="check_printer_relations_no_circular"),
    )

    printer = relationship("Printer", foreign_keys=[printer_id], uselist=False)
    related_printer = relationship("Printer", foreign_keys=[related_printer_id], uselist=False)

if __name__ == "__main__":
    # generate the SQL code
    engine = create_engine(f"sqlite:///./db/dilapp_{__version__}.db")
    Base.metadata.create_all(engine)
