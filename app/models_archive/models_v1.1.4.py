"""
Modèle V1.1.4 de la base de données de DIL-App

Commentaires: modèle finalisé

Printer > Person OK

birth_date / birth_city OK

birth_city > clé étrangère vers city (a evaluer) OK

City

garder old_label mais succeptible de virer OK
ajouter department_id (id_insee Vincent) OK
pas de old_label_department mais label_department (celui de parinet) OK
+ ajouter tous les ids nécéssaires (geonames, dicotopo, wikidata, wikipedia, bnf) OK

Adress > PersonAddress

Evaluer pour Address si on garde ou pas (selon analyse + mail de parinet) sinon tous dans Printer_address_relation

Pour image pareil : a quel point une même ressource iconographique est relié a plusieurs imprimeurs


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

__version__ = "1.1.4"

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
    __order__ = ""
    PARTNER = "associé"
    SPONSOR = "parrain"
    SUCCESSOR = "successeur"
    PREDECESSOR = "prédécesseur"


class AddressType(BaseEnum):
    """Types d'adresses

    :param PRO: adresse professionnelle
    :param PERSO: adresse personnelle
    """
    __order__ = "PRO PERSO"
    PRO = "professionnelle"
    PERSO = "personnelle"


# -- drupal_main tables --

class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    # label du référentiel INSEE
    label = Column(String, nullable=False)
    # label de Parinet (a evaluer sinon dans label)
    old_label = Column(String, nullable=False)
    # label department de Parinet
    department = Column(String, nullable=True)
    # identifiant vincent dans référentiel INSEE
    department_id = Column(String, nullable=True)
    long_lat = Column(String, nullable=True)
    geoname_id = Column(String, nullable=True)
    wikidata_item_id = Column(String, nullable=True)
    wipedia_url = Column(String, nullable=True)
    dicotopo_uri = Column(String, nullable=True)
    databnf_ark = Column(String, nullable=True)
    viaf_id = Column(String, nullable=True)
    siaf_id = Column(String, nullable=True)

    # Relations
    addresses = relationship('Address', back_populates='city')
    patents = relationship('Patent', back_populates='city')

class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)

    # Relation avec VilleDepartement
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship('City', back_populates='address')


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    lastname = Column(String, nullable=False, unique=False)
    firstnames = Column(String, nullable=True, unique=False)
    birth_date = Column(String, nullable=True, unique=False)
    birth_city = Column(Integer, ForeignKey('city.id'), nullable=True, unique=False)
    personal_information = Column(String, nullable=True, unique=False)
    professional_information = Column(String, nullable=True, unique=False)
    comment = Column(String, nullable=True, unique=False)

    # Relation avec les adresses
    addresses = relationship('Address', back_populates='person')

    # Relation avec les brevets
    patents = relationship('Patent', back_populates='person')

    # Créé le
    created_at = Column(DateTime, default=datetime.datetime.now)
    # Mis à jour le
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class Patent(Base):
    __tablename__ = 'patents'

    id = Column(Integer, primary_key=True)
    date_start = Column(String)
    date_end = Column(String)
    # bibliographie et sources
    references = Column(String)
    comment = Column(String)

    # Relation avec Imprimeur
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship('Person', back_populates='patents')

    # Relation avec VilleDepartement
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship('City', back_populates='patents')

    relations = relationship('PatentRelations', back_populates='patents')

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)
    reference_url = Column(String)
    local_path = Column(String)
    iiif_url = Column(String)

# -- relations tables --

class PersonAddresses(Base):
    __tablename__ = 'person_adresses'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    address_id = Column(Integer, ForeignKey('address.id'))
    patent_id = Column(Integer, ForeignKey('patents.id'))
    type = Column(Enum(AddressType), nullable=False)
    date_occupation = Column(String)

    # Relations
    printer = relationship('Person', back_populates='person')
    address = relationship('Address', back_populates='address')
    patent = relationship('Brevet', back_populates='patents')


class PersonImages(Base):
    __tablename__ = 'person_images'

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    image_id = Column(Integer, ForeignKey('images.id'))

    is_pinned = Column(Boolean, default=False, nullable=False)

    # Relations
    person = relationship('Person', back_populates='person')
    image = relationship('Image', back_populates='images')

    # unique constraint for is_pinned : un imprimeur ne peut avoir qu'une seule image épinglée donc un seul is_pinned sur True
    """
    __table_args__ = (
        UniqueConstraint('imprimeur_id', 'is_pinned', name='uq_imprimeur_image_pinned',
                         condition=Column('is_pinned') == True),
    )
    """

class PatentRelations(Base):
    __tablename__ = 'patent_relations'

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
