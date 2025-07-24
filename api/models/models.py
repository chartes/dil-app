import os
import base64
import datetime
import enum
import mimetypes
import random
import re
import string
import uuid
import time
from functools import wraps
from unidecode import unidecode

from sqlalchemy import (Column,
                        Integer,
                        String,
                        DateTime,
                        Enum,
                        event,
                        ForeignKey,
                        Boolean)
from sqlalchemy.orm import (relationship,
                            declared_attr,
                            sessionmaker)
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin
from werkzeug.security import (generate_password_hash,
                               check_password_hash)
import jwt

from ..database import (BASE,
                        session)
from .constants import (countries_ISO_3166,
                        departments_INSEE_code,
                        type_patent_relations,
                        roles_user)
from ..index_fts.index_conf import st
from ..index_fts.index_utils import prepare_content

from api.config import settings

# DB models constants and utilities
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff"}

params_default_relations = lambda bp, delete=True: {
    'back_populates': bp,
    'cascade': "all, delete, delete-orphan" if delete else "",
    # 'passive_deletes': delete
}

def handle_index(method):
    """
    Decorator to handle the index during sqlalchemy events.
    """

    @wraps(method)
    def wrapper(cls, mapper, connection, target):
        """
        Wrapper to handle the index.
        """
        try:
            ix = st.open_index()
            method(cls, mapper, connection, target, ix)
            ix.close()
        except Exception:
            pass

    return wrapper


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


###########################################################
# ~~~~~~~~~~~~~~~~~~~ > Enum tables < ~~~~~~~~~~~~~~~~~~~ #

class BaseEnum(enum.Enum):
    @classmethod
    def values(cls):
        """Renvoie une liste des valeurs de l'énumération."""
        return [item.value for item in cls]

    @classmethod
    def create_enum(cls, name, data):
        """
        Méthode de classe pour créer dynamiquement un Enum basé sur un dictionnaire.

        :param name: Nom de l'énumération
        :param data: Dictionnaire contenant les clés et valeurs
        :return: Une sous-classe dynamique de BaseEnum
        """
        enum_members = {
            key.replace(' ', '_').replace('-', '_').replace('\'', ''): value
            for key, value in data.items()
        }
        return enum.Enum(name, enum_members, type=cls)

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


def _get_enum_values(enum_class):
    return (item.value for item in enum_class)


# -- Enum Base Class --
PatentRelationType = BaseEnum.create_enum("PatentRelationType", type_patent_relations)
CountryISOEnum = BaseEnum.create_enum("CountryISOEnum", countries_ISO_3166)
DepartementINSEEEnum = BaseEnum.create_enum("DepartementINSEEEnum", departments_INSEE_code)
RolesUserEnum = BaseEnum.create_enum("RolesUserEnum", roles_user)


###############################################################
# ~~~~~~~~~~~~~~~~~~~ > Abstract tables < ~~~~~~~~~~~~~~~~~~~ #

class AbstractBase(BASE):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)

    @declared_attr
    def _id_dil(cls):
        return Column(String(25), nullable=False, unique=True,
                      default=lambda: cls.generate_unique_id(session, cls, cls.__prefix__))

    @staticmethod
    def generate_unique_id(session, cls, prefix):
        """Génère un ID unique et vérifie l'absence de doublons."""
        while True:
            new_id = generate_random_uuid(prefix=prefix, provider="dil")
            if not session.query(cls).filter(cls._id_dil == new_id).first():
                return new_id

    @staticmethod
    def generate_img_name(file_path: str) -> str:
        """Génère le nom de fichier de l'image avec l'extension correcte."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            raise ValueError(f"Impossible de détecter le type MIME pour le fichier : {file_path}")

        extension = mimetypes.guess_extension(mime_type)
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"L'extension {extension} n'est pas autorisée. Autorisées : {', '.join(ALLOWED_EXTENSIONS)}")

        return extension

    @classmethod
    def correct_markup(cls, target):
        """Corrige les balises HTML pour les champs textuels des objets Person."""
        if isinstance(target, Person):
            target.personal_information = correct_br_markup_quill(target.personal_information or "")
            target.professional_information = correct_br_markup_quill(target.professional_information or "")
            target.comment = correct_br_markup_quill(target.comment or "")
        if isinstance(target, Patent):
            target.references = correct_br_markup_quill(target.references or "")

    @classmethod
    def check_person_exists(cls, session, target):
        """Vérifie qu'un brevet ne peut être créé que si la personne associée existe."""
        if isinstance(target, Patent) and not session.query(Person).filter_by(id=target.person_id).first():
            raise IntegrityError("L'imprimeur est requis pour créer un brevet.", params={}, orig=None)


    @classmethod
    def set_img_name(cls, target):
        """Attribue le nom de l'image si un fichier est fourni."""
        if isinstance(target, Image):
            image_name = getattr(target, "img_name", None)
            # detect extension from file path
            if image_name and image_name != "unknown.jpg":
                extension = cls.generate_img_name(image_name)
                new_id_dil = cls.generate_unique_id(session, cls, cls.__prefix__)
                target._id_dil = new_id_dil
                target.img_name = f"{new_id_dil}{extension}"
                # rename the file
                os.rename(os.path.join(settings.IMAGE_STORE, image_name),
                          os.path.join(settings.IMAGE_STORE, target.img_name))

    @classmethod
    def check_img_patent_relations_pinned(cls, target, session):
        """S'assure qu'une seule image d'un brevet est `pinned`."""
        if isinstance(target, PatentHasImages):
            if target.is_pinned:  # Si la nouvelle relation est `pinned`
                # Récupérer toutes les autres relations liées au même brevet
                session.query(PatentHasImages).filter(
                PatentHasImages.patent_id == target.patent_id,
                PatentHasImages.id != target.id  # Exclure l'image actuelle
            ).update({"is_pinned": False})  # Désactiver le flag `pinned`
                session.commit()

    @classmethod
    def destroy_img(cls, target):
        """Détruit l'image associée à l'objet."""
        if isinstance(target, Image):
            if target.img_name and target.img_name != "unknown.jpg":
                os.remove(os.path.join(settings.IMAGE_STORE, target.img_name))

    @classmethod
    @handle_index
    def update_person_fts_index_after_update(cls, mapper, connection, target, ix):
        """Update the index after update a person"""
        if cls.__tablename__ == "persons":
            writer = ix.writer()
            clean_text = prepare_content(target)
            lastname = target.lastname or ""
            firstnames = target.firstnames or ""
            lastname = unidecode(lastname or "").lower().encode('utf-8').decode('utf-8')
            firstnames = unidecode(firstnames or "").lower().encode('utf-8').decode('utf-8')
            writer.add_document(
                id_dil=str(target._id_dil).encode('utf-8').decode('utf-8'),
                lastname=lastname,
                firstnames=firstnames,
                content=clean_text.encode('utf-8').decode('utf-8'),
                content_ngram=unidecode(clean_text).lower().encode('utf-8').decode('utf-8'),
                firstnames_lastname=f"{' '.join(firstnames.split(','))} {lastname}"
            )

            writer.commit()

    @classmethod
    @handle_index
    def insert_person_fts_index_after_insert(cls, mapper, connection, target, ix):
        """Insert a reference in the index"""
        if cls.__tablename__ == "persons":
            writer = ix.writer()
            clean_text = prepare_content(target)
            lastname = target.lastname or ""
            firstnames = target.firstnames or ""
            lastname = unidecode(lastname or "").lower().encode('utf-8').decode('utf-8')
            firstnames = unidecode(firstnames or "").lower().encode('utf-8').decode('utf-8')
            writer.add_document(
                id_dil=str(target._id_dil).encode('utf-8').decode('utf-8'),
                lastname=lastname,
                firstnames=firstnames,
                content=clean_text.encode('utf-8').decode('utf-8'),
                content_ngram=unidecode(clean_text).lower().encode('utf-8').decode('utf-8'),
                firstnames_lastname=f"{' '.join(firstnames.split(','))} {lastname}"
            )

            writer.commit()

    @classmethod
    @handle_index
    def delete_person_fts_index_after_delete(cls, mapper, connection, target, ix):
        """Delete a reference from the index"""
        with sessionmaker(bind=connection)() as session:
            if cls.__tablename__ == "persons":
                writer = ix.writer()
                writer.delete_by_term('id_dil', str(target._id_dil))
                writer.commit()


@event.listens_for(AbstractBase, "before_insert", propagate=True)
@event.listens_for(AbstractBase, "before_update", propagate=True)
def before_insert_or_update(_, connection, target):
    with sessionmaker(bind=connection)() as session:
        target.correct_markup(target)
        target.check_person_exists(session, target)
        target.set_img_name(target)
        target.check_img_patent_relations_pinned(target, session)


@event.listens_for(AbstractBase, "after_insert", propagate=True)
def after_insert(mapper, connection, target):
    with sessionmaker(bind=connection)() as session:
        target.insert_person_fts_index_after_insert(mapper, session, target)

@event.listens_for(AbstractBase, "after_update", propagate=True)
def after_update(mapper, connection, target):
    with sessionmaker(bind=connection)() as session:
        target.update_person_fts_index_after_update(mapper, session, target)

@event.listens_for(AbstractBase, "after_delete", propagate=True)
def after_delete(mapper, connection, target):
    with sessionmaker(bind=connection)() as session:
        target.destroy_img(target)
        target.delete_person_fts_index_after_delete(mapper, session, target)


class AbstractVersion(AbstractBase):
    __abstract__ = True

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
class User(UserMixin, BASE):
    """User model"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    email = Column(String(120), index=True, unique=True, nullable=False)
    role = Column(Enum(*_get_enum_values(RolesUserEnum)), nullable=False, default="READER")
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @staticmethod
    def generate_password():
        from .models_utils import pwd_generator
        return pwd_generator()

    def set_password(self, password):
        """Set a password hashed"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        """Generate a token for reset password"""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            settings.FLASK_SECRET_KEY, algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password_token(token):
        """Verify if token is valid"""
        try:
            id_tok = jwt.decode(token,
                                settings.FLASK_SECRET_KEY,
                                algorithms=['HS256'])['reset_password']
        except jwt.exceptions.InvalidTokenError:
            return
        return session.query(User).get(id_tok)

    @staticmethod
    def add_default_user(in_session):
        """Add default user to database"""
        admin = User()
        admin.username = settings.FLASK_ADMIN_NAME
        admin.email = settings.FLASK_ADMIN_MAIL
        admin.password_hash = settings.FLASK_ADMIN_ADMIN_PASSWORD
        admin.role = "ADMIN"
        in_session.add(admin)
        in_session.commit()



class Person(AbstractVersion):
    """Imprimeurs et lithographes identifiés.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de la personne forgé (avec le prefixe person_) [REQ.]
    :type _id_dil: STRING(25)
    :param lastname: Nom de famille de la personne. [REQ.]
    :type lastname: STRING
    :param firstnames: Prénoms de la personne. [OPT.]
    :type firstnames: STRING
    :param birth_date: Date de naissance de la personne. [OPT.]
    :type birth_date: STRING(25)
    :param birth_city_label: Ville de naissance de la personne. Il peut s'agir du label ancien. [OPT.]
    :type birth_city_label: STRING
    :param birth_city_id: Identifiant de la ville de naissance de la personne. [OPT.]
    :type birth_city_id: FOREIGN_KEY(City)
    :param personal_information: Informations personnelles sur la personne. [OPT.]
    :type personal_information: STRING
    :param professional_information: Informations professionnelles sur la personne. [OPT.]
    :type professional_information: STRING
    :param comment: Commentaire/mémo éditorial sur la personne. [OPT.]
    :type comment: STRING
    """
    __tablename__ = "persons"
    __prefix__ = "person"

    # -------------------------------------------------------

    lastname = Column(String, nullable=False, unique=False)
    firstnames = Column(String, nullable=True, unique=False, default=None)
    birth_date = Column(String(25), nullable=True, unique=False, default=None)
    birth_city_label = Column(String, nullable=True, unique=False, default=None)
    birth_city_id = Column(Integer, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, unique=False,
                           default=None)
    personal_information = Column(String, nullable=True, unique=False, default=None)
    professional_information = Column(String, nullable=True, unique=False, default=None)
    comment = Column(String, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    city = relationship("City",
                        **params_default_relations("persons", delete=False),
                        foreign_keys=[birth_city_id])
    patents = relationship("Patent",
                           order_by="Patent.date_start.asc()",
                           **params_default_relations("person", delete=True))
    addresses_relations = relationship("PersonHasAddresses",
                                       **params_default_relations("person_addresses", delete=True))
    related_patents = relationship("PatentHasRelations",
                                   foreign_keys="PatentHasRelations.person_id",
                                   cascade="all, delete-orphan",
                                   # overlaps="person"
                                   )
    linked_patents = relationship("PatentHasRelations",
                                  foreign_keys="PatentHasRelations.person_related_id",
                                  cascade="all, delete-orphan",
                                  # overlaps="person_related"
                                  )

    # birth_cities = relationship("City",
    #                            foreign_keys="Person.birth_city_id",
    #                            back_populates="persons")

    def __repr__(self):
        return f"<Imprimeur : {self.id} | {self.lastname} {self.firstnames}>"

    def __str__(self):
        return f"{self.lastname} {self.firstnames}"




class Patent(AbstractVersion):
    """Brevets des imprimeurs et lithographes identifiés.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique du brevet forgé (avec le prefixe patent_) [REQ.]
    :type _id_dil: STRING(25)
    :param drupal_nid: Identifiant de l'ancien nœud Drupal associé. Indication de développement. [OPT.]
    :type drupal_nid: INTEGER
    :param person_id: Identifiant de l'imprimeur/lithographe associé. [REQ.]
    :type person_id: FOREIGN_KEY(Person)
    :param city_label: Ville de dépôt du brevet. Il peut s'agir du label ancien. [OPT.]
    :type city_label: STRING
    :param city_id: Identifiant de la ville de dépôt du brevet. [OPT.]
    :type city_id: FOREIGN_KEY(City)
    :param date_start: Date de début de validité du brevet. [OPT.]
    :type date_start: STRING
    :param date_end: Date de fin de validité du brevet. [OPT.]
    :type date_end: STRING
    :param references: Références bibliographiques du brevet. [OPT.]
    :type references: STRING
    :param comment: Commentaire/mémo éditorial sur le brevet. [OPT.]
    :type comment: STRING
    """
    __tablename__ = "patents"
    __prefix__ = "patent"

    drupal_nid = Column(Integer, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=False)
    city_label = Column(String, nullable=True, unique=False, default=None)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="SET NULL"), nullable=True, unique=False, default=None)
    date_start = Column(String, nullable=True, unique=False, default=None)
    date_end = Column(String, nullable=True, unique=False, default=None)
    references = Column(String, nullable=True, unique=False, default=None)
    comment = Column(String, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    person = relationship("Person",
                          **params_default_relations("patents", delete=False),
                          foreign_keys=[person_id])
    city = relationship("City",
                        **params_default_relations("patents", delete=False),
                        foreign_keys=[city_id])
    patent_relations = relationship("PatentHasRelations",
                                    **params_default_relations("patent", delete=True))
    addresses_relations = relationship("PatentHasAddresses",
                                       **params_default_relations("patent_addresses", delete=True), viewonly=True)
    images_relations = relationship("PatentHasImages",
                                    **params_default_relations("patent_images", delete=True), viewonly=True)

    addresses = relationship("Address",
                             secondary="patent_has_addresses",
                             backref="addresses",
                             lazy="dynamic",
                             overlaps="patents",
                             )

    images = relationship("Image",
                          secondary="patent_has_images",
                          backref="patents",
                          lazy="dynamic",
                          overlaps="patents",
                          )

    def __repr__(self):
        return f"<Brevet : {self.id} | {self._id_dil} ; person : {self.person_id} ; city : {self.city_id}>"

    def __str__(self):
        return f"{self._id_dil} ; {self.person_id} ; {self.city_id}"


class City(AbstractVersion):
    """Référentiel des villes.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de la ville forgé (avec le prefixe city_) [REQ.]
    :type _id_dil: STRING(25)
    :param label: Nom de la ville. Il peut s'agir du label ancien. [REQ.]
    :type label: STRING
    :param country_iso_code: Code ISO 3166 du Pays de la ville. Obligatoire [via un enum] [OPT.]
    :type country_iso_code: STRING
    :param long_lat: Longitute et latitude de la ville - Opt. [OPT.]
    :type long_lat: STRING
    :param insee_fr_code: Code INSEE de la ville française - Opt. [OPT.]
    :type insee_fr_code: STRING
    :param insee_fr_department_code: Code INSEE du département français - Opt. [via un enum]
    :type insee_fr_department_code: STRING
    :param insee_fr_department_label: Label du département français - Opt. [OPT.]
    :type insee_fr_department_label: STRING
    :param geoname_id: Identifiant de la ville dans la base GeoNames - Opt. [OPT.]
    :type geoname_id: STRING
    :param wikidata_item_id: Identifiant de la ville dans Wikidata - Opt. [OPT.]
    :type wikidata_item_id: STRING
    :param dicotopo_item_id: Identifiant de la ville dans Dicotopo - Opt. [OPT.]
    :type dicotopo_item_id: STRING
    :param databnf_ark: Identifiant de la ville dans data.bnf.fr - Opt. [OPT.]
    :type databnf_ark: STRING
    :param viaf_id: Identifiant de la ville dans VIAF - Opt. [OPT.]
    :type viaf_id: STRING
    :param siaf_id: Identifiant de la ville dans SIAF - Opt. [OPT.]
    :type siaf_id: STRING
    """
    __tablename__ = "cities"
    __prefix__ = "city"

    # -------------------------------------------------------

    label = Column(String, nullable=False, unique=False)
    country_iso_code = Column(Enum(*_get_enum_values(CountryISOEnum)), nullable=False, unique=False,
                              default=CountryISOEnum.France.value)
    long_lat = Column(String, nullable=True, unique=False, default=None)
    insee_fr_code = Column(String, nullable=True, unique=False, default=None)
    insee_fr_department_code = Column(Enum(*_get_enum_values(DepartementINSEEEnum)), nullable=True, unique=False,
                                      default="DEP_00")
    insee_fr_department_label = Column(String, nullable=True, unique=False, default=None)
    geoname_id = Column(String, nullable=True, unique=False, default=None)
    wikidata_item_id = Column(String, nullable=True, unique=False, default=None)
    dicotopo_item_id = Column(String, nullable=True, unique=False, default=None)
    databnf_ark = Column(String, nullable=True, unique=False, default=None)
    viaf_id = Column(String, nullable=True, unique=False, default=None)
    siaf_id = Column(String, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    addresses = relationship('Address', **params_default_relations("city", delete=False))
    patents = relationship("Patent", **params_default_relations("city", delete=False))
    persons = relationship("Person", **params_default_relations("city", delete=False))

    def __repr__(self):
        return f"< Ville : {self.id} | {self.label} ({self.insee_fr_department_code}, {self.country_iso_code}) >"

    def __str__(self):
        return self.__repr__()


class Address(AbstractVersion):
    """Référentiel des adresses.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de l'adresse forgé (avec le prefixe address_) [REQ.]
    :type _id_dil: STRING(25)
    :param label: Label de l'adresse. [REQ.]
    :type label: STRING
    :param city_label: Ville de l'adresse. Il peut s'agir du label ancien. [REQ.]
    :type city_label: STRING
    :param city_id: Identifiant de la ville de l'adresse. [OPT.]
    :type city_id: FOREIGN_KEY(City)
    """
    __tablename__ = 'addresses'
    __prefix__ = "address"

    # -------------------------------------------------------

    label = Column(String, nullable=False, unique=False, default='inconnue')
    city_label = Column(String, nullable=False, unique=False, default=None)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    city = relationship('City',
                        **params_default_relations("addresses", delete=False))

    persons_relations = relationship("PersonHasAddresses",
                                     **params_default_relations("address_persons", delete=True))
    patents_relations = relationship("PatentHasAddresses",
                                     **params_default_relations("address_patents", delete=True),
                                     viewonly=True)

    # patents = relationship("PatentHasAddresses",
    #                                cascade="all, delete-orphan",
    #                                back_populates="address_patents")

    def __repr__(self):
        return f"< Adresse : {self.id} | {self.label} ({self.city_label}) >"

    def __str__(self):
        return self.__repr__()


class Image(AbstractVersion):
    """Référentiel des images.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de l'image forgé (avec le prefixe img_) [REQ.]
    :type _id_dil: STRING(25)
    :param label: Label de l'image. [REQ.]
    :type label: STRING
    :param reference_url: URL de référence de l'image. [OPT.]
    :type reference_url: STRING
    :param img_name: Nom de l'image. [OPT.]
    """
    __tablename__ = 'images'
    __prefix__ = "img"

    # -------------------------------------------------------

    label = Column(String, nullable=False, unique=False)
    reference_url = Column(String, nullable=False, unique=False, default='unknown_url')
    img_name = Column(String, nullable=True, unique=False, default='unknown.jpg')
    iiif_url = Column(String, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    patent_relations = relationship('PatentHasImages',
                                    **params_default_relations("image_patents", delete=True), viewonly=True)

    @property
    def card_meta(self):
        return {
            "label": self.label,
            "on_iiif": self.iiif_url if self.iiif_url is not None else "unk",
            "on_url_ref": self.reference_url if self.reference_url != "unknown_url" else "unk",
            "on_filestore": "true" if self.img_name != "unknown.jpg" else "false"
        }

    def __repr__(self):
        url_ref = ""
        iiif = ""
        if self.card_meta['on_url_ref'] != "unk":
            url_ref = f" | url_ref={self.card_meta['on_url_ref']}"
        if self.card_meta['on_iiif'] != "unk":
            iiif = f" | iiif={self.card_meta['on_iiif']}"
        return f"< Image : {self.id} | label={self.label}{url_ref}{iiif} >"

    def __str__(self):
        return self.__repr__()


##################################################################
# ~~~~~~~~~~~~~~~~~~~ > Association tables < ~~~~~~~~~~~~~~~~~~~ #
class PatentHasRelations(AbstractVersion):
    """Table d'association entre imprimeurs et brevets.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de la relation entre brevets forgé (avec le prefixe patent_relation_) [REQ.]
    :type _id_dil: STRING(25)
    :param patent_id: Identifiant du brevet associé. [REQ.]
    :type patent_id: FOREIGN_KEY(Patent)
    :param person_id: Identifiant de l'imprimeur associé. [REQ.]
    :type person_id: FOREIGN_KEY(Person)
    :param person_related_id: Identifiant de l'imprimeur associé (second). [REQ.]
    :type person_related_id: FOREIGN_KEY(Person)
    :param type: Type de relation entre les imprimeurs. [REQ.]
    :type type: ENUM(PatentRelationType)
    """
    __tablename__ = 'patent_has_relations'
    __prefix__ = "patent_relation"

    # -------------------------------------------------------

    patent_id = Column(Integer, ForeignKey("patents.id", ondelete='CASCADE'), nullable=False, unique=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=False)
    person_related_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=False)
    type = Column(Enum(*_get_enum_values(PatentRelationType)), nullable=False, unique=False)

    # -------------------------------------------------------

    # Relations
    patent = relationship("Patent",
                          **params_default_relations("patent_relations", delete=False),
                          foreign_keys=[patent_id])
    person = relationship("Person", foreign_keys=[person_id], overlaps="related_patents")
    person_related = relationship("Person", foreign_keys=[person_related_id], overlaps="linked_patents")


class PatentHasAddresses(AbstractVersion):
    """Table d'association entre brevets et adresses.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de la relation entre brevets et adresses forgé (avec le prefixe patent_address_) [REQ.]
    :type _id_dil: STRING(25)
    :param patent_id: Identifiant du brevet associé. [REQ.]
    :type patent_id: FOREIGN_KEY(Patent)
    :param address_id: Identifiant de l'adresse associée. [REQ.]
    :type address_id: FOREIGN_KEY(Address)
    :param date_occupation: Date d'occupation de l'adresse par le brevet. [OPT.]
    :type date_occupation: STRING
    """
    __tablename__ = 'patent_has_addresses'
    __prefix__ = "patent_address"

    # -------------------------------------------------------

    patent_id = Column(Integer, ForeignKey("patents.id"), nullable=False, unique=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False, unique=False)
    date_occupation = Column(String, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    patent_addresses = relationship("Patent",
                                    **params_default_relations("addresses_relations", delete=False),
                                    viewonly=True
                                    )
    address_patents = relationship("Address",
                                   **params_default_relations("patents_relations", delete=False),
                                   viewonly=True
                                   )
    # patent_addresses = relationship("Patent",
    #                      **params_default_relations("addresses", delete=False))
    # address_patents = relationship("Address",
    #                       **params_default_relations("patents", delete=False))


class PersonHasAddresses(AbstractVersion):
    """Table d'association entre imprimeurs et adresses.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de la relation entre imprimeurs et adresses forgé (avec le prefixe person_address_) [REQ.]
    :type _id_dil: STRING(25)
    :param person_id: Identifiant de l'imprimeur associé. [REQ.]
    :type person_id: FOREIGN_KEY(Person)
    :param address_id: Identifiant de l'adresse associée. [REQ.]
    :type address_id: FOREIGN_KEY(Address)
    :param date_occupation: Date d'occupation de l'adresse par l'imprimeur. [OPT.]
    :type date_occupation: STRING
    """
    __tablename__ = 'person_has_addresses'
    __prefix__ = "person_address"

    # -------------------------------------------------------

    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False, unique=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False, unique=False)
    date_occupation = Column(String, nullable=True, unique=False, default=None)
    comment = Column(String, nullable=True, unique=False, default=None)

    # -------------------------------------------------------

    # Relations
    person_addresses = relationship("Person",
                                    **params_default_relations('addresses_relations', delete=False),
                                    foreign_keys=[person_id])
    address_persons = relationship("Address",
                                   **params_default_relations('persons_relations', delete=False),
                                   foreign_keys=[address_id])


class PatentHasImages(AbstractVersion):
    """Table d'association entre brevets et images.

    :param id: Clé primaire autoincrémenté. [REQ.]
    :type id: PRIMARY KEY
    :param _id_dil: Identifiant unique de la relation entre brevets et images forgé (avec le prefixe patent_image_) [REQ.]
    :type _id_dil: STRING(25)
    :param patent_id: Identifiant du brevet associé. [REQ.]
    :type patent_id: FOREIGN_KEY(Patent)
    :param image_id: Identifiant de l'image associée. [REQ.]
    :type image_id: FOREIGN_KEY(Image)
    :param is_pinned: Indique si l'image est épinglée pour le brevet. [OPT.]
    :type is_pinned: BOOLEAN
    """
    __tablename__ = "patent_has_images"
    __prefix__ = "patent_image"

    # -------------------------------------------------------
    patent_id = Column(Integer, ForeignKey("patents.id"), nullable=False, unique=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False, unique=False)
    is_pinned = Column(Boolean, default=False, nullable=False, unique=False)

    # -------------------------------------------------------

    # Relations
    patent_images = relationship("Patent",
                                 **params_default_relations("images_relations", delete=False), viewonly=True)
    image_patents = relationship("Image",
                                 **params_default_relations("patent_relations", delete=False), viewonly=True)