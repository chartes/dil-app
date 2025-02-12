"""
Modèle de la base de données de DIL-App
"""

import enum
import datetime
import random
import uuid
import base64
import string
import mimetypes
import re

from sqlalchemy import (Column,
                        DateTime,
                        Boolean,
                        ForeignKey,
                        Integer,
                        String,
                        Enum,
                        event,
                        create_engine)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (sessionmaker,
                            relationship,
                            declarative_base,
                            declared_attr,
                            )

import pandas as pd
import numpy as np

from .database import (BASE,
                       session)

__version__ = ""


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff"}

__mapping_prefix__ = {
    "Person": "person",
    "Patent": "patent",
    "City": "city",
    "Address": "address",
    "Image": "img"
}


# -- DB utils functions --
def generate_random_uuid(prefix: str, provider: str = "") -> str:
    """Generates a random UUID and converts it to a URL-safe Base64 encoded
    bytes string and decoded to a Unicode string.
    """
    uuid_bytes = uuid.uuid4().bytes
    base64_encoded = base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')
    # replace punctuation with random characters
    # cut uuid to 8 (but possibility to increase or decrease)
    # this represents ≈ 10,376,800,670,380,293 possible identifier combinations
    random_chars = ''.join(
        random.choice(string.ascii_letters) if c in string.punctuation else c for c in base64_encoded[:8])
    return f"{prefix}_{provider}_{random_chars}" if provider else f"{prefix}_{random_chars}"


def correct_br_markup_quill(old_html: str):
    """replace <p><br><p> in quill default by <br />"""
    return re.sub(r"<p><br></p>", "<br />", str(old_html))


# -- Enum Base Class --
class BaseEnum(enum.Enum):
    @classmethod
    def values(cls):
        return [item.value for item in cls]

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

# -- Enum Base Class --
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


# -- Abstract Base Classes --
class AbstractActions(BASE):
    __abstract__ = True

    # _id_dil = Column(String(25), nullable=False, unique=True)

    @declared_attr
    def _id_dil(cls):
        print("cls: ", cls)
        return Column(String(25), nullable=False, unique=True)

    @staticmethod
    def generate_unique_id(session, cls, prefix):
        """Génère un identifiant unique pour _id_dil en évitant les collisions."""
        is_exist = True
        new_id = None
        while is_exist:
            new_id = generate_random_uuid(prefix=prefix, provider="dil")
            # Vérifier si l'ID existe déjà
            is_exist = session.query(cls).filter(cls._id_dil == new_id).first() is not None
        return new_id

    @classmethod
    def before_insert_create_id_ref(cls, mapper, connection, target):
        """Génère un ID unique pour _id_dil avant chaque insertion."""
        if (not target._id_dil) or (target._id_dil is None):  # Si _id_dil est vide, génère un ID
            print(f"==> Generating unique ID for {target.__class__.__name__}")
            try:
                prefix = getattr(target, "__prefix__", "default")
                # Utilisation de la connexion pour ouvrir une session temporaire
                with sessionmaker(bind=connection)() as session:
                    target._id_dil = cls.generate_unique_id(session, cls, prefix)
            except Exception as e:
                print(f"Erreur lors de la génération de l'ID : {e}")
                raise

    @classmethod
    def before_insert_correct_markup(cls, mapper, connection, target):
        print(target.__class__.__name__)
        if target.__class__.__name__ in ['Person']:
            target.personal_information = correct_br_markup_quill(target.personal_information)
            target.professional_information = correct_br_markup_quill(target.professional_information)
            target.comment = correct_br_markup_quill(target.comment)

    @classmethod
    def before_create_patent_check_if_person_exists(cls, mapper, connection, target):
        """Vérifie si l'imprimeur existe avant de créer un brevet."""
        if target.__class__.__name__ in ['Patent']:
            person = session.query(Person).filter(Person.id == target.person_id).first()
            if person is None:
                raise IntegrityError("L'imprimeur est requis pour créer un brevet.", params={}, orig=None)


@event.listens_for(AbstractActions, "before_insert", propagate=True)
def before_insert(mapper, connection, target):
    print("before insert")
    target.before_create_patent_check_if_person_exists(mapper, connection, target)
    target.before_insert_correct_markup(mapper, connection, target)
    target.before_insert_create_id_ref(mapper, connection, target)


@event.listens_for(AbstractActions, "before_update", propagate=True)
def before_update(mapper, connection, target):
    print("before_update")
    target.before_create_patent_check_if_person_exists(mapper, connection, target)
    target.before_insert_correct_markup(mapper, connection, target)


class AbstractVersion(AbstractActions):
    __abstract__ = True

    # def __init__(self):
    #    super(AbstractActions, self).__init__()

    # created_at = Column(DateTime, default=datetime.datetime.now())
    # updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    # last_editor = Column(String, nullable=True, default='admin')

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.datetime.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    @declared_attr
    def last_editor(cls):
        return Column(String, nullable=True, default='admin')


###########################################################
# ~~~~~~~~~~~~~~~~~~~ > Main tables < ~~~~~~~~~~~~~~~~~~~ #
class Person(AbstractVersion):
    """Table des imprimeurs.
    """
    __tablename__ = "persons"
    __prefix__ = "person"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)

    # -------------------------------------------------------
    lastname = Column(String, nullable=False, unique=False)
    firstnames = Column(String, nullable=True, unique=False)
    birth_date = Column(String(25), nullable=True, unique=False)
    birth_city_label = Column(String, nullable=True, unique=False)
    birth_city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, unique=False)
    personal_information = Column(String, nullable=True, unique=False)
    professional_information = Column(String, nullable=True, unique=False)
    comment = Column(String, nullable=True, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    patents = relationship("Patent",
                           foreign_keys="Patent.person_id",
                           cascade="all, delete-orphan",
                           order_by="Patent.date_start.asc()",
                           lazy="dynamic",
                           back_populates="person")
    birth_cities = relationship("City",
                                foreign_keys="Person.birth_city_id",
                                back_populates="persons")

    related_patents = relationship("PatentHasRelations",
                                   foreign_keys="PatentHasRelations.person_id",
                                   cascade="all, delete-orphan",
                                   overlaps="person")

    linked_patents = relationship("PatentHasRelations",
                                  foreign_keys="PatentHasRelations.person_related_id",
                                  cascade="all, delete-orphan",
                                  overlaps="person_related")
    person_addresses = relationship("PersonHasAddresses",
                                    cascade="all, delete-orphan",
                                    back_populates="person")

    def __repr__(self):
        return f"<Imprimeur : {self.id} | {self.lastname} {self.firstnames}>"


class Patent(AbstractVersion):
    """Table des brevets.
    """
    __tablename__ = "patents"
    __prefix__ = "patent"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)
    # -------------------------------------------------------
    # note: old id from drupal
    drupal_nid = Column(Integer, nullable=True, unique=False)
    # note: relation with person
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=False)
    date_start = Column(String, nullable=True, unique=False)
    date_end = Column(String, nullable=True, unique=False)
    references = Column(String, nullable=True, unique=False)
    comment = Column(String, nullable=True, unique=False)
    city_label = Column(String, nullable=True, unique=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    # Relations
    person = relationship("Person",
                          foreign_keys="Patent.person_id",
                          back_populates="patents")
    city = relationship("City",
                        foreign_keys="Patent.city_id",
                        back_populates="patents")
    patent_images = relationship('PatentHasImages',
                                 cascade="all, delete-orphan",
                                 back_populates='patent')
    patent_relations = relationship("PatentHasRelations",
                                    cascade="all, delete-orphan",
                                    back_populates="patent")

    addresses = relationship(
        "Address",
        cascade="all, delete",
        secondary="patent_has_addresses",
        backref="patents"
    )

    # Relation directe avec les adresses via la table intermédiaire
    """
    addresses = relationship(
        "Address",
        secondary="patent_has_addresses",
        back_populates="patents",
        overlaps="patent_addresses"
    )
    """



class City(AbstractVersion):
    __tablename__ = "cities"
    __prefix__ = "city"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)
    # -------------------------------------------------------
    label = Column(String, nullable=False, unique=False)
    # Code ISO 3166 du Pays de la ville - Obligatoire [via un enum]
    country_iso_code = Column(String, nullable=False, unique=False, default="FR")
    # Longitute et latitude de la ville - Opt.
    long_lat = Column(String, nullable=True, unique=False)
    # Code INSEE de la ville française - Opt.
    insee_fr_code = Column(String, nullable=True, unique=False)
    # Code INSEE du département français - Opt. [via un enum]
    insee_fr_department_code = Column(String, nullable=True, unique=False)
    # Label INSEE department français  - Opt. [via un enum]
    insee_fr_department_label = Column(String, nullable=True, unique=False)
    # Identifiants de désambiguïsation
    geoname_id = Column(String, nullable=True)
    wikidata_item_id = Column(String, nullable=True)
    dicotopo_item_id = Column(String, nullable=True)
    databnf_ark = Column(String, nullable=True)
    viaf_id = Column(String, nullable=True)
    siaf_id = Column(String, nullable=True)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    # Relations
    addresses = relationship('Address', back_populates='city')
    patents = relationship("Patent", back_populates="city")
    persons = relationship("Person", back_populates="birth_cities")

    def __repr__(self):
        return f"< Ville : {self.id} | {self.label} ({self.insee_fr_department_code}, {self.country_iso_code}) >"

    # def __str__(self):
    #    return self.label


class Address(AbstractVersion):
    __tablename__ = 'addresses'
    __prefix__ = "address"

    id = Column(Integer, primary_key=True)
    _id_dil = Column(String(25), nullable=False, unique=True)

    # -------------------------------------------------------
    label = Column(String, nullable=False, default='inconnue', unique=False)
    city_label = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    # Relations
    city = relationship('City', back_populates='addresses')

    patents = relationship("Patent",
                            cascade="all, delete",
                                    secondary="patent_has_addresses",
                                    backref="addresses"
                                    )
    person_addresses = relationship("PersonHasAddresses",
                                    cascade="all, delete-orphan",
                                    back_populates="address")

    # Relation avec les brevets
    #patents = relationship(
    #    "Patent",
    #    secondary="patent_has_addresses",
    #    back_populates="addresses",
    #    overlaps="patent_addresses"
    #)

    def __repr__(self):
        return f"< Adresse : {self.id} | {self.label} ({self.city_label}) >"


class Image(AbstractActions):
    __tablename__ = 'images'
    __prefix__ = "img"

    id = Column(Integer, primary_key=True)
    _id_dil = Column(String(25), nullable=False, unique=True)
    # -------------------------------------------------------
    label = Column(String, nullable=False, unique=False)
    reference_url = Column(String, nullable=True, unique=False)
    # only: jpg, jpeg, tiff, png
    img_name = Column(String, nullable=True, unique=False)
    iiif_url = Column(String, nullable=True, unique=False)
    # > Relations
    patent_images = relationship('PatentHasImages', back_populates='image')
    # -------------------------------------------------------
    added_at = Column(DateTime, default=datetime.datetime.now())
    added_by = Column(String, nullable=True, default='admin')

    def generate_img_name_with_extension(self, file_path: str) -> str:
        """Génère img_name en détectant automatiquement l'extension."""
        mime_type, encoding = mimetypes.guess_type(file_path)
        if not mime_type:
            raise ValueError(f"Impossible de détecter le type MIME pour le fichier : {file_path}")

        # Extraire l'extension à partir du type MIME
        extension = mimetypes.guess_extension(mime_type)
        if not extension:
            raise ValueError(f"Impossible de déterminer l'extension pour le type MIME : {mime_type}")

        # Vérifier si l'extension est autorisée
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"L'extension {extension} n'est pas autorisée. Extensions autorisées : {', '.join(sorted(ALLOWED_EXTENSIONS))}")

        # Retourner le nom complet
        return f"{self._id_dil}{extension}"

    def __repr__(self):
        return f"{self.label}"


@event.listens_for(Image, "before_insert")
@event.listens_for(Image, "before_update")
def set_img_name(mapper, connection, target):
    """
    Définit automatiquement img_name en détectant l'extension du fichier.
    """
    # Simule le chemin du fichier uploadé (par exemple, depuis un champ de formulaire)
    uploaded_file_path = getattr(target, "uploaded_file_path", None)

    if uploaded_file_path:  # Si un fichier est fourni
        try:
            target.img_name = target.generate_img_name_with_extension(uploaded_file_path)

        except ValueError as e:
            print(f"Erreur lors de la génération du nom de fichier : {e}")
            target.img_name = None
    else:  # Si aucun fichier n'est fourni
        target.img_name = None


###########################################################
# ~~~~~~~~~~~~~~~~~~~ > Relation tables < ~~~~~~~~~~~~~~~~~~~ #
class PatentHasRelations(AbstractVersion):
    __tablename__ = 'patent_has_relations'
    __prefix__ = "patent_relation"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)
    # -------------------------------------------------------
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False, unique=False)
    person_related_id = Column(Integer, ForeignKey('persons.id'), nullable=False, unique=False)
    patent_id = Column(Integer, ForeignKey('patents.id'), nullable=False, unique=False)
    type = Column(Enum(PatentRelationType), nullable=False, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    # Relations
    patent = relationship("Patent", back_populates="patent_relations")
    person = relationship("Person", foreign_keys=[person_id], overlaps="related_patents")
    person_related = relationship("Person", foreign_keys=[person_related_id], overlaps="linked_patents")
    # -------------------------------------------------------

    # TODO: Contraintes a implémenter...
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


class PatentHasAddresses(AbstractVersion):
    __tablename__ = 'patent_has_addresses'
    __prefix__ = "patent_address"

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)

    # -------------------------------------------------------
    patent_id = Column(Integer, ForeignKey('patents.id', ondelete="CASCADE"), nullable=False, unique=False)
    address_id = Column(Integer, ForeignKey('addresses.id', ondelete="CASCADE"), nullable=False, unique=False)
    date_occupation = Column(String, nullable=True, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    #patent = relationship('Patent',
    #                      back_populates='addresses')
    #address = relationship('Address',
    #                       back_populates='patents')



class PersonHasAddresses(AbstractVersion):
    __tablename__ = 'person_has_addresses'
    __prefix__ = "person_address"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)

    # -------------------------------------------------------
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False, unique=False)
    address_id = Column(Integer, ForeignKey('addresses.id'), nullable=False, unique=False)
    date_occupation = Column(String, nullable=True, unique=False)
    comment = Column(String, nullable=True, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    # Relations
    person = relationship('Person', back_populates='person_addresses')  # Correction
    address = relationship('Address', back_populates='person_addresses')

    def __repr__(self):
        return f"< Adresse : {self.address.id} | {self.address.label} ({self.address.city_label}) >"


class PatentHasImages(AbstractVersion):
    __tablename__ = 'patent_has_images'
    __prefix__ = "patent_image"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    _id_dil = Column(String(25), nullable=False, unique=True)

    # -------------------------------------------------------
    patent_id = Column(Integer, ForeignKey('patents.id'), nullable=False, unique=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False, unique=False)
    is_pinned = Column(Boolean, default=False, nullable=False, unique=False)

    # created_at = AbstractVersion.created_at
    # updated_at = AbstractVersion.updated_at
    # last_editor = AbstractVersion.last_editor

    # Relations
    patent = relationship('Patent', back_populates='patent_images')
    image = relationship('Image', back_populates='patent_images')


# Événement pour valider la contrainte
@event.listens_for(PatentHasImages, "before_insert")
@event.listens_for(PatentHasImages, "before_update")
def validate_single_pinned_image(mapper, connection, target):
    """
    Valide qu'un brevet n'a pas déjà une image épinglée avant l'insertion ou la mise à jour.
    """
    if target.is_pinned:
        session = sessionmaker(bind=connection.engine)()
        # Vérifie si une autre image est déjà épinglée pour le même brevet
        existing_pinned = session.query(PatentHasImages).filter_by(
            patent_id=target.patent_id, is_pinned=True
        ).first()

        # Si une image est déjà épinglée et qu'elle est différente de la cible
        if existing_pinned and existing_pinned.id != target.id:
            raise ValueError(
                f"Le brevet {target.patent_id} possède déjà une image épinglée (ID : {existing_pinned.id})."
            )


if __name__ == "__main__":
    from contextlib import contextmanager
    from scripts.dil_dtypes_spec import DTYPE_SPEC

    session = sessionmaker()

    base = declarative_base()

    engine = create_engine(f"sqlite:///../db/DIL{__version__}.db")
    base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)


    @contextmanager
    def get_session():
        session = Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()


    def load_tsv_to_db(file_path, table_model):
        try:
            with get_session() as session:
                print(f"==> Loading data from {file_path} to {table_model.__tablename__} table.")

                data = pd.read_csv(file_path, sep='\t', encoding='utf-8',
                                   dtype=DTYPE_SPEC.get(table_model.__tablename__, None))

                data = data.replace({np.nan: None})

                if '_id_dil' not in data.columns:
                    data.insert(0, '_id_dil', None)

                data['_id_dil'] = data['_id_dil'].apply(
                    lambda x: x if x else generate_random_uuid(prefix=table_model.__prefix__, provider="dil")
                )

                records = data.to_dict(orient='records')

                session.bulk_insert_mappings(table_model, records)

                print(f"==> {len(records)} rows inserted in {table_model.__tablename__} table.")

        except FileNotFoundError as e:
            print(f"Erreur : Fichier introuvable : {file_path}")

        except Exception as e:
            print(f"Erreur lors de l'importation dans la table {table_model.__tablename__}: {e}")


    base_path_data_tables = "../../data/tables_to_migrate/final_rev/tables/"
    base_path_data_relations = "../../data/tables_to_migrate/final_rev/relations/"
    ORDER_IMPORT = [
        (f'{base_path_data_tables}table_city.tsv', City),
        (f'{base_path_data_tables}table_address.tsv', Address),
        (f'{base_path_data_tables}table_person.tsv', Person),
        (f'{base_path_data_tables}table_patent.tsv', Patent),
        (f'{base_path_data_tables}table_image_prepared.csv', Image),

        (f'{base_path_data_relations}patent_has_relations.tsv', PatentHasRelations),
        (f'{base_path_data_relations}patent_has_addresses.tsv', PatentHasAddresses),
        (f'{base_path_data_relations}person_has_addresses.tsv', PersonHasAddresses),
        (f'{base_path_data_relations}patent_has_images.tsv', PatentHasImages)
    ]

    for file_path, table_model in ORDER_IMPORT:
        load_tsv_to_db(file_path, table_model)
