"""
Modèle de la base de données de DIL-App
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
                        Text,
                        Float)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

__version__ = "vstable"

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


class PatentRelationType(BaseEnum):
    """Types de relations entre brevets

    :param PARTNER: associé
    :param SPONSOR: parrain
    :param SUCCESSOR: successeur
    :param PREDECESSOR: prédécesseur
    """
    __order__ = "PARTNER SPONSOR SUCCESSOR PREDECESSOR"
    PARTNER = "associé"
    SPONSOR = "parrain"
    SUCCESSOR = "successeur"
    PREDECESSOR = "prédécesseur"

# -- drupal_main tables --

class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True, autoincrement=True)
    _id_dil = Column(String, nullable=False, unique=True)
    # Label de la ville (autant que possible aligné sur l'Insee)
    label = Column(String, nullable=False, unique=False)
    # Code ISO 3166 du Pays de la ville - Obligatoire [via un enum]
    country_iso_code = Column(String, nullable=False, unique=False)
    # Longitute et latitude de la ville - Opt.
    long_lat = Column(String, nullable=True)
    # Code INSEE de la ville française - Opt.
    insee_fr_code = Column(String, nullable=True, unique=False)
    # Code INSEE du département français - Opt. [via un enum]
    insee_fr_department_code = Column(String, nullable=True, unique=False)
    # Label INSEE department français  - Opt. [via un enum]
    insee_fr_label_department = Column(String, nullable=True, unique=False)
    # Identifiants de désambiguïsation
    geoname_id = Column(String, nullable=True)
    wikidata_item_id = Column(String, nullable=True)
    dicotopo_item_id = Column(String, nullable=True)
    databnf_ark = Column(String, nullable=True)
    viaf_id = Column(String, nullable=True)
    siaf_id = Column(String, nullable=True)

    # Relations
    addresses = relationship('Address', back_populates='city')
    patents = relationship('Patent', back_populates='city')

class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    _id_dil = Column(String, nullable=False)

    label = Column(String, nullable=False)
    city_label = Column(String, nullable=False)

    # Relation avec VilleDepartement
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship('City', back_populates='address')




class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    _id_dil = Column(String, nullable=False)
    lastname = Column(String, nullable=False, unique=False)
    firstnames = Column(String, nullable=True, unique=False)
    birth_date = Column(String, nullable=True, unique=False)
    birth_city_id = Column(Integer, ForeignKey('city.id'), nullable=True, unique=False)
    birth_city_label = Column(String, nullable=True, unique=False)
    personal_information = Column(String, nullable=True, unique=False)
    professional_information = Column(String, nullable=True, unique=False)
    comment = Column(String, nullable=True, unique=False)

    # Relation avec les adresses
    addresses = relationship('Address', back_populates='person')

    # Relation avec la ville de naissance
    birth_city = relationship('City', back_populates='person')

    # Relation avec les brevets
    patents = relationship('Patent', back_populates='person')

    # Créé le
    created_at = Column(DateTime, default=datetime.datetime.now)
    # Mis à jour le
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    # last editor
    last_editor = Column(String, nullable=True)

class Patent(Base):
    __tablename__ = 'patents'

    id = Column(Integer, primary_key=True)
    _id_dil = Column(String, nullable=False)
    drupal_nid = Column(Integer, nullable=False)
    date_start = Column(String)
    date_end = Column(String)

    # bibliographie et sources
    references = Column(String)
    comment = Column(String)

    # Relation avec Imprimeur
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person', back_populates='patents')

    # Relation avec VilleDepartement
    city_label = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship('City', back_populates='patents')

    relations = relationship('PatentHasRelations', back_populates='patents')

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    _id_dil = Column(String, nullable=False)
    label = Column(String, nullable=False)
    reference_url = Column(String)
    local_path = Column(String)
    iiif_url = Column(String)

# -- relations tables --

class PersonHasAddresses(Base):
    __tablename__ = 'person_has_addresses'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    address_id = Column(Integer, ForeignKey('address.id'))
    date_occupation = Column(String)

    # Relations
    person = relationship('Person', back_populates='addresses')
    address = relationship('Address', back_populates='persons')


class PatentHasAddresses(Base):
    __tablename__ = 'patent_has_addresses'

    id = Column(Integer, primary_key=True)
    patent_id = Column(Integer, ForeignKey('patents.id'))
    address_id = Column(Integer, ForeignKey('address.id'))
    date_occupation = Column(String)

    # Relations
    patent = relationship('Patent', back_populates='addresses')
    address = relationship('Address', back_populates='patents')


class PatentHasImages(Base):
    __tablename__ = 'patent_has_images'

    id = Column(Integer, primary_key=True)
    patent_id = Column(Integer, ForeignKey('patents.id'))
    image_id = Column(Integer, ForeignKey('images.id'))

    is_pinned = Column(Boolean, default=False, nullable=False)

    # Relations
    patent = relationship('Patent', back_populates='patents')
    image = relationship('Image', back_populates='images')

    # unique constraint for is_pinned : un imprimeur ne peut avoir qu'une seule image épinglée donc un seul is_pinned sur True
    """
    __table_args__ = (
        UniqueConstraint('imprimeur_id', 'is_pinned', name='uq_imprimeur_image_pinned',
                         condition=Column('is_pinned') == True),
    )
    """

class PatentHasRelations(Base):
    __tablename__ = 'patent_has_relations'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    person_related_id = Column(Integer, ForeignKey('person.id'))
    patent_id = Column(Integer, ForeignKey('patents.id'))
    type = Column(Enum(PatentRelationType), nullable=False)

    """
    __table_args__ = (
        # Un imprimeur ne peut avoir qu'un seul prédécesseur
        UniqueConstraint('imprimeur_id', 'type', name='u_predecesseur',
                         condition=Column('type') == 'prédécesseur'),
        # Un imprimeur ne peut avoir qu'un seul successeur
        UniqueConstraint('imprimeur_id', 'type', name='u_successeur',
                         condition=Column('type') == 'successeur'),
    )
    """



if __name__ == "__main__":
    # generate the SQL code
    engine = create_engine(f"sqlite:///./db/dilapp_{__version__}.db")
    Base.metadata.create_all(engine)
