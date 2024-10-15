"""
Modèle V1.1.3 de la base de données de DIL-App

Commentaires:
    Refonte totale suite à la réunion avec E. Parinet


    - Est-ce qu'on ajoute l'arrondissement dans l'entité ville ?
    - On inclut un CV professionnel dans imprimeur ? dans commentaires de l'imprimeur ?
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

__version__ = "1.1.3"

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


class BrevetRelationType(BaseEnum):
    """Types de relations entre brevets

    :param ASSOCIE: associé
    :param PARRAIN: parrain
    :param SUCCESSEUR: successeur
    :param PREDECESSEUR: prédécesseur
    """
    __order__ = ""
    ASSOCIE = "associé"
    PARRAIN = "parrain"
    SUCCESSEUR = "successeur"
    PREDECESSEUR = "prédécesseur"


class AdresseType(BaseEnum):
    """Types d'adresses

    :param PRO: adresse professionnelle
    :param PERSO: adresse personnelle
    """
    __order__ = "PRO PERSO"
    PRO = "professionnelle"
    PERSO = "personnelle"


# -- drupal_main tables --

class Ville(Base):
    __tablename__ = 'ville'

    id = Column(Integer, primary_key=True)
    ville = Column(String, nullable=False)
    departement = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    dicotopo_uri = Column(String)

    # Relations
    adresses = relationship('Adresse', back_populates='ville')
    brevets = relationship('Brevet', back_populates='ville')


class Adresse(Base):
    __tablename__ = 'adresse'

    id = Column(Integer, primary_key=True)
    libelle = Column(String)

    # Relation avec VilleDepartement
    ville_id = Column(Integer, ForeignKey('ville.id'))
    ville = relationship('Ville', back_populates='adresses')


class Imprimeur(Base):
    __tablename__ = 'imprimeur'

    id = Column(Integer, primary_key=True)
    nom = Column(String, nullable=False, unique=False)
    prenoms = Column(String, nullable=False, unique=False)
    date_naissance = Column(String, nullable=True, unique=False)
    ville_naissance = Column(String, nullable=True, unique=False)
    infos_personnelles = Column(String, nullable=True, unique=False)
    infos_professionnelles = Column(String, nullable=True, unique=False)
    commentaire = Column(String, nullable=True, unique=False)

    # Relation avec les adresses
    adresses = relationship('Adresse', back_populates='imprimeur')

    # Relation avec les brevets
    brevets = relationship('Brevet', back_populates='imprimeur')

    # Relation avec les iconographies
    iconographies = relationship('Iconographie', back_populates='imprimeur')

    # Créé le
    created_at = Column(DateTime, default=datetime.datetime.now)
    # Mis à jour le
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

class Brevet(Base):
    __tablename__ = 'brevet'

    id = Column(Integer, primary_key=True)
    date_debut = Column(String)
    date_fin = Column(String)
    biblio_sources = Column(String)
    commentaire = Column(String)

    # Relation avec Imprimeur
    imprimeur_id = Column(Integer, ForeignKey('imprimeur.id'))
    imprimeur = relationship('Imprimeur', back_populates='brevets')

    # Relation avec VilleDepartement
    ville_id = Column(Integer, ForeignKey('ville.id'))
    ville = relationship('Ville', back_populates='brevets')

    relations = relationship('BrevetRelations', back_populates='brevet')

class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    titre = Column(String, nullable=False)
    url_reference = Column(String)
    chemin_local = Column(String)
    lien_iiif = Column(String)

# -- relations tables --

class ImprimeurAdresses(Base):
    __tablename__ = 'imprimeur_adresses'

    id = Column(Integer, primary_key=True)
    imprimeur_id = Column(Integer, ForeignKey('imprimeur.id'))
    adresse_id = Column(Integer, ForeignKey('adresse.id'))
    brevet_id = Column(Integer, ForeignKey('brevet.id'))
    type = Column(Enum(AdresseType), nullable=False)
    date_occupation = Column(String)

    # Relations
    imprimeur = relationship('Imprimeur', back_populates='adresses')
    adresse = relationship('Adresse', back_populates='imprimeur')
    brevet = relationship('Brevet', back_populates='adresses')


class ImprimeurImages(Base):
    __tablename__ = 'imprimeur_images'

    id = Column(Integer, primary_key=True)
    imprimeur_id = Column(Integer, ForeignKey('imprimeur.id'))
    image_id = Column(Integer, ForeignKey('image.id'))

    is_pinned = Column(Boolean, default=False, nullable=False)

    # Relations
    imprimeur = relationship('Imprimeur', back_populates='iconographies')
    image = relationship('Image', back_populates='imprimeur')

    # unique constraint for is_pinned : un imprimeur ne peut avoir qu'une seule image épinglée donc un seul is_pinned sur True
    """
    __table_args__ = (
        UniqueConstraint('imprimeur_id', 'is_pinned', name='uq_imprimeur_image_pinned',
                         condition=Column('is_pinned') == True),
    )
    """

class BrevetRelations(Base):
    __tablename__ = 'brevet_relations'

    id = Column(Integer, primary_key=True)
    imprimeur__id = Column(Integer, ForeignKey('imprimeur.id'))
    imprimeur_relie_id = Column(Integer, ForeignKey('imprimeur.id'))
    brevet_id = Column(Integer, ForeignKey('brevet.id'))
    type = Column(Enum(BrevetRelationType), nullable=False)

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
