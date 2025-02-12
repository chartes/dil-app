"""
"""
import os

from werkzeug.utils import secure_filename
from flask import url_for, jsonify, request
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from flask_admin import expose
from flask_admin.form import ImageUploadField, thumbgen_filename

from wtforms import Form
from wtforms.fields import StringField, FieldList
from wtforms import TextAreaField
from wtforms.widgets import TextArea

from markupsafe import Markup
from sqlalchemy import or_

from .validators import (is_valid_date,
                         is_valid_url)
from ..models.models import *
from .widget import QuillWidget
from .formaters import (_format_label_form_with_tooltip,
                        _format_link_add_model)
from .model_handler import PrinterModelChangeHandler
from ..config import settings

def prefix_name(obj, file_data):
    parts = os.path.splitext(file_data.filename)
    return secure_filename('file-%s%s' % parts)

class CustomForm(Form):
    dynamic_printers = FieldList(StringField('Imprimeur'), min_entries=1)
    dynamic_relation_types = FieldList(StringField('Type de relation'), min_entries=1)


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class CityAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, **options):
        super(CityAjaxModelLoader, self).__init__(name, options)

    def format(self, model):
        if model is None:
            return None
        if isinstance(model, int):
            # find city by primary key
            model = session.query(City).get(model)
        return (model.id, repr(model))

    def get_one(self, pk):
        return session.query(City).get(pk)

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        search_term = query.strip().lower()
        return session.query(City).filter(City.label.ilike(f"%{search_term}%")).offset(offset).limit(limit).all()


class ImageAjaxModelLoader(QueryAjaxModelLoader):
    def format(self, model):
        if model is None:
            return None
        if isinstance(model, PatentHasImages):
            model = session.query(Image).filter(Image.id == model.image_id).first()
        return (model.id,
                repr(model))

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        search_term = query.strip().lower()
        return (
            session.query(Image)
            .filter(Image.label.ilike(f"%{search_term}%"))
            .offset(offset)
            .limit(limit)
            .all()
        )


class GlobalModelView(ModelView):
    """Global & Shared parameters for the model views."""
    column_display_pk = True
    can_view_details = True
    can_set_page_size = False
    action_disallowed_list = ['delete']
    # list_template = 'admin/list.html'
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True


class PrinterView(GlobalModelView):
    """View for the person model."""
    edit_template = 'admin/edit.printer.html'
    create_template = 'admin/edit.printer.html'
    column_auto_select_related = True
    # list_template = 'admin/person_list.html'
    # details_template = 'admin/person_details.html'
    # Define column that will be displayed in list view

    column_list = ["id",
                   '_id_dil',
                   "lastname",
                   "firstnames",
                   "birth_date",
                   "birth_city_label",
                   "birth_city_id",
                   "personal_information",
                   "professional_information",
                   "comment",
                   "created_at",
                   "updated_at",
                   "last_editor"]

    # Overrides column labels
    column_labels = {"id": "ID",
                     "_id_dil": "ID DIL",
                     "lastname": "Nom",
                     "firstnames": "Prénom(s)",
                     "birth_date": "Date de naissance",
                     "birth_city_label": "Ville de naissance",
                     "birth_city_id": "Ville de naissance (référentiel)",
                     "personal_information": "Informations personnelles",
                     "professional_information": "Informations professionnelles",
                     "comment": "Commentaire",
                     "addresses_relations": "Adresses personnelles",
                     "patents": "Brevets",
                     "created_at": "Créé le",
                     "updated_at": "Modifié le",
                     "last_editor": "Dernier éditeur",
                     'city': "Ville de naissance (référentiel)",
                     "date_start": "Début du brevet",
                     "date_end": "Fin du brevet",
                     }
    column_searchable_list = ["lastname",
                              "firstnames",
                              "birth_city_label"]

    column_formatters = {
        'birth_city_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("city.details_view", id=m.birth_city_id)}">'
                f'{m.city}</a>'
            ) if m.city else "(Aucune ville)"
        )
    }

    inline_models = [
        (PersonHasAddresses, {
            "form_columns": ["id",
                             "address_persons",
                             "date_occupation"],
            "column_labels": {
                "address_persons": "Adresses",
                "date_occupation": "Date d'occupation",
            },
            "form_args": {
                "address_persons": {
                    "label": _format_label_form_with_tooltip(label="Adresse",
                                                                comment="Adresses personnelles de l'imprimeur."),
                    "description": _format_link_add_model(description="une nouvelle adresse",
                                                            href='/dil/admin/address/new/?url=/dil/admin/address/')
                },
                "date_occupation": {
                    "validators": [is_valid_date],
                    "label": _format_label_form_with_tooltip(label="Date d'occupation",
                                                             comment="Première date d'occupation de l'adresse. "
                                                                     "Au format <b>AAAA-MM-JJ</b>, "
                                                                     "<b>AAAA-MM</b> ou <b>AAAA</b>. "
                                                                     "Ajouter le signe <b>~</b> devant pour "
                                                                     "indiquer une date approximative."),
                    "description": "Format requis : <b>AAAA-MM-JJ</b>, <b>AAAA-MM</b> ou <b>AAAA</b>. "
                                   "Ajouter le signe <b>~</b> devant pour indiquer une date approximative."
                }
            },
            "form_ajax_refs": {
                "address_persons": QueryAjaxModelLoader(
                    "address_persons", session, Address, fields=["label"], page_size=10,
                    placeholder="Commencer la saisie puis sélectionner une adresse...",
                    allow_blank=True
                )
            }
        }),

        (Patent, {
            "form_columns": [
                "id",
                "date_start",
                "date_end",
                "city_label",
                "city",
                "references",
                "comment",
                "addresses",
                "relation_container",
                "images",
            ],
            "column_labels": {
                "date_start": "Début du brevet",
                "date_end": "Fin du brevet",
                "city_label": "Ville",
                "city": "Ville (référentiel)",
                "references": "Bibliographie / Sources",
                "comment": "Mémo (édition)",
                "addresses": "Adresses professionnelles",
                "images": "Images"

            },
            "form_overrides": {
                "references": QuillWidget,

            },
            "form_extra_fields": {
                "relation_container": StringField(
                    label="Relations avec imprimeurs",
                    widget=TextArea(),  # Placeholding container
                    render_kw={"id": "relation-container"}
                )
            },
            "form_widget_args": {
                "images": {"onchange": "addPreview(this);", "class": "select2-image"},
                "relation_container": {"onchange": "makeRelation(this)", "class": "relation-container-attach"}
            },
            "form_ajax_refs": {
                "city": QueryAjaxModelLoader(
                    "city", session, City, fields=["label"], page_size=10,
                    placeholder="Commencer la saisie puis sélectionner une ville...",
                    allow_blank=True
                ),
                "addresses": QueryAjaxModelLoader(
                    "addresses", session, Address, fields=["label"], page_size=10,
                    placeholder="Commencer la saisie puis sélectionner une ou plusieurs adresses...",
                    allow_blank=True
                ),
                "images": ImageAjaxModelLoader(
                    "images", session, Image, fields=["label"], page_size=10,
                    placeholder="Commencer la saisie puis sélectionner une ou plusieurs images...",
                    allow_blank=True,
                )
            },
            "form_args": {

                "date_start": {
                    "validators": [is_valid_date],
                    "label": _format_label_form_with_tooltip(label="Début du brevet",
                                                             comment="Début du brevet. "
                                                                     "Au format <b>AAAA-MM-JJ</b>, "
                                                                     "<b>AAAA-MM</b> ou <b>AAAA</b>. "
                                                                     "Ajouter le signe <b>~</b> devant pour "
                                                                     "indiquer une date approximative."),
                    "description": "Format requis : <b>AAAA-MM-JJ</b>, <b>AAAA-MM</b> ou <b>AAAA</b>. "
                                   "Ajouter le signe <b>~</b> devant pour indiquer une date approximative."
                },
                "date_end": {
                    "validators": [is_valid_date],
                    "label": _format_label_form_with_tooltip(label="Fin du brevet",
                                                             comment="Fin du brevet. "
                                                                     "Au format <b>AAAA-MM-JJ</b>, "
                                                                     "<b>AAAA-MM</b> ou <b>AAAA</b>. "
                                                                     "Ajouter le signe <b>~</b> devant pour "
                                                                     "indiquer une date approximative."),
                    "description": "Format requis : <b>AAAA-MM-JJ</b>, <b>AAAA-MM</b> ou <b>AAAA</b>. "
                                   "Ajouter le signe <b>~</b> devant pour indiquer une date approximative."
                },
                "city_label": {
                    "label": _format_label_form_with_tooltip(label="Ville",
                                                             comment="Libellé de la ville du brevet. "
                                                                     "Peut correspondre au toponyme ancien.",
                                                             ),
                    "description": "exemples : Verdun-sur-le-Doubs (Saône-et-Loire) ; "
                                   "Clermont-Ferrand (Puy-de-Dôme) ; Paris etc."
                },
                "city": {
                    "label": _format_label_form_with_tooltip(label="Ville (référentiel)",
                                                                comment="Ville du brevet dans le référentiel."),
                    "description": _format_link_add_model(description="une nouvelle ville",
                                                            href='/dil/admin/city/new/?url=/dil/admin/city/')
                },
                "addresses": {
                    "label": _format_label_form_with_tooltip(label="Adresses professionnelles",
                                                             comment="Adresses professionnelles liées au brevet."),
                    "description": _format_link_add_model(description="une nouvelle adresse",
                                                          href='/dil/admin/address/new/?url=/dil/admin/address/')
                },
                "images": {
                    "label": _format_label_form_with_tooltip(label="Images",
                                                                comment="Images liées au brevet."),
                    "description": _format_link_add_model(description="une nouvelle image",
                                                            href='/dil/admin/image/new/?url=/dil/admin/image/')
                }


            },


        }),

    ]

    # Form attributes
    form_columns = [
        "lastname",
        "firstnames",
        "birth_date",
        "birth_city_label",
        "city",
        "personal_information",
        "professional_information",
        "comment"
    ]

    form_excluded_columns = ('id', '_id_dil', 'created_at', 'updated_at', 'last_editor')

    # Define form widget arguments
    form_widget_args = {
        "firstnames": {
            "class": "input-select-tag-form-1 form-control",
        },
    }

    form_ajax_refs = {
        'city': QueryAjaxModelLoader(
            'city', session, City, fields=['label'], page_size=10,
            placeholder='Commencer la saisie puis sélectionner une ville...',
            allow_blank=True
        )
    }

    form_args = {
        "lastname": {
            "label": _format_label_form_with_tooltip(label="Nom",
                                                     comment="Nom de l'imprimeur.")
        },
        "city": {
            "label": _format_label_form_with_tooltip(label="Ville de naissance (référentiel)",
                                                     comment="Ville de naissance de l'imprimeur. "
                                                             "Peut correspondre au toponyme ancien."),
            "description": _format_link_add_model(description="une nouvelle ville",
                                                  href='/dil/admin/city/new/?url=/dil/admin/city/')
        },
        "firstnames": {
            "label": _format_label_form_with_tooltip(label="Prénom(s)",
                                                     comment="Prénom(s) de l'imprimeur. "
                                                             "Appuyer sur '<b>,</b>' ou '<b>tab</b>' pour ajouter un prénom."),
            "description": "Appuyer sur '<b>,</b>' ou '<b>tab</b>' pour ajouter un prénom."
        },
        "birth_date": {
            "validators": [is_valid_date],
            "label": _format_label_form_with_tooltip(label="Date de naissance",
                                                     comment="Date de naissance de l'imprimeur. "
                                                             "Au format <b>AAAA-MM-JJ</b>, "
                                                             "<b>AAAA-MM</b> ou <b>AAAA</b>. "
                                                             "Ajouter le signe <b>~</b> devant pour "
                                                             "indiquer une date approximative."),
            "description": "Format requis : <b>AAAA-MM-JJ</b>, <b>AAAA-MM</b> ou <b>AAAA</b>. "
                           "Ajouter le signe <b>~</b> devant pour indiquer une date approximative."
        },
        "birth_city_label": {
            "label": _format_label_form_with_tooltip(label="Ville de naissance",
                                                     comment="Libellé de la ville de naissance. "
                                                             "Peut correspondre au toponyme ancien."),
            "description": "exemples : Verdun-sur-le-Doubs (Saône-et-Loire) ; Clermont-Ferrand (Puy-de-Dôme) ; Paris etc."
        },

    }

    def on_model_change(self, form, model, is_created):
        # overrides classical on_model_change and after_model_change
        # of Flask-Admin because we need to handle the form data with
        # custom elements that come from the js.
        # 1. instantiate the handler for custom actions
        handler = PrinterModelChangeHandler(
            session=self.session,
            model=model,
            form=form
        )
        # 2. some tests and validation if needed on form data
        handler.on_model_change()
        # 3. call the after_model_change method for
        # update, create or delete data in the database
        # when model is created or updated
        handler.after_model_change(is_created=is_created)

    def get_list_columns(self):
        """Return list of columns to display in list view."""
        return super(PrinterView, self).get_list_columns()

    def get_list_form(self):
        """Return list of columns to display in list form."""
        return super(PrinterView, self).get_list_form()

    # Expose custom routes for printer view
    # for Ajax requests

    @expose('/get_image_details/', methods=['GET', 'POST'])
    def get_image_details(self):
        """Retrieves details of an image from the database"""
        if request.method in ['GET', 'POST']:
            image_id = request.args.get('id')  # Récupère l'ID de l'image depuis les paramètres GET
            patent_id = request.args.get('patent_id')  # Récupère l'ID du brevet depuis les paramètres GET
            if not image_id:
                return jsonify({'error': 'No ID provided'}), 400
            # Cherchez l'image dans la base
            image = session.query(Image).filter_by(id=image_id).first()
            # chercher si l'image est pinned à un brevet dans une relation
            try:
                is_pinned = session.query(PatentHasImages).filter_by(image_id=image_id,
                                                                     patent_id=patent_id).first().is_pinned
            except AttributeError:
                is_pinned = False
            if not image:
                return jsonify({'error': 'Image not found'}), 404

            img_name = image.img_name
            return jsonify({
                'id': image.id,
                'label': image.label,
                'img_name': image.img_name,
                'img_url': url_for("static", filename=f"images_store/{img_name}") if img_name else img_name,
                'img_iiif_url': image.iiif_url,
                'is_pinned': is_pinned
            })

    @expose('/get_printers', methods=['GET'])
    def ajax_printers(self):
        """Retrieves a list of printers for Select2."""
        search = request.args.get('q', '')  # Récupère le terme de recherche
        query = (
            session.query(Person)
            .filter(
                or_(
                    Person.lastname.ilike(f"%{search.lower()}%"),
                    Person.firstnames.ilike(f"%{search.lower()}%")
                )
            )
            .order_by(Person.lastname, Person.firstnames)  # Trier par nom et prénom
        ).limit(20)  # Limiter les résultats

        results = [{"id": person.id, "text": repr(person)} for person in query]
        print(results)
        # Ajouter une clé "results" pour que Select2 comprenne le format
        return jsonify(results)

    @expose('/get_printer/<int:person_id>', methods=['GET'])
    def ajax_printer(self, person_id):
        """Retrieves details of a printer from the database."""
        person = (
            session.query(Person)
            .filter(Person.id == person_id)
            .first()
        )
        return jsonify({
            "id": person_id,
            "text": repr(person)
        })

    @expose('/get_patent_relations/<int:person_id>', methods=['GET'])
    def get_patent_relations(self, person_id):
        """Retrieves relations for a printer."""
        # retrieve all patents for the printer
        patents = session.query(Patent).filter_by(person_id=person_id).all()
        patents_id = [p.id for p in patents]
        # Grouper les relations par `patent_id`
        grouped_relations = {}
        for pid in patents_id:
            # Récupère les relations de brevet pour l'imprimeur spécifié et son brevet
            relations = (
                session.query(PatentHasRelations)
                .filter(PatentHasRelations.person_id == person_id, PatentHasRelations.patent_id == pid)
                .all()
            )
            if pid not in grouped_relations:
                grouped_relations[pid] = []
            for relation in relations:
                # find key in type_patent_relations dictionary
                relation_type = [k for k, v in type_patent_relations.items() if v == relation.type][0]
                grouped_relations[pid].append({
                    "person_related_id": relation.person_related_id,
                    "relation_type": relation_type  # Convertir Enum en chaîne
                })

        return jsonify(grouped_relations)


class ImageView(GlobalModelView):
    """View for the image model."""
    edit_template = 'admin/edit.image.html'
    create_template = 'admin/edit.image.html'
    column_list = [
        "id",
        "_id_dil",
        "label",
        "img_name",
        "reference_url",
        "iiif_url",
        "added_at",
        "added_by",
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "label": "Libellé",
        "img_name": "Image",
        "reference_url": "URL de référence (opt.)",
        "iiif_url": "URL IIIF (opt.)",
        "added_at": "Ajouté le",
        "added_by": "Ajouté par",
    }
    column_formatters = {
        'img_name': lambda v, c, m, p: Markup(
            f'<img src="{url_for("static", filename=f"images_store/{m.img_name}")}" '
            'style="max-width: 200px; max-height: 200px;">'
            if m.img_name != 'unknown.jpg' else f'<img src="{m.iiif_url}" style="max-width: 200px; max-height: 200px;">'
        ),
        'reference_url': lambda v, c, m, p: Markup(
            f'<a href="{m.reference_url}" target="_blank">{m.reference_url}</a>'
            if m.reference_url else '<p>Pas d\'URL de référence</p>'
        ),
        'iiif_url': lambda v, c, m, p: Markup(
            f'<a href="{m.iiif_url}" target="_blank">{m.iiif_url}</a>'
            if m.iiif_url else '<p>Pas d\'URL IIIF</p>'
        ),
    }

    form_columns = [
        "label",
        "img_name",
        "reference_url",
        "iiif_url",
    ]

    form_excluded_columns = ('id', '_id_dil', 'created_at', 'updated_at', 'last_editor', 'patent_relations')

    form_args = {
        "label": {
            "label": "Libellé",
            "description": "Libellé de l'image. "
                           "Exemple : <b>Vue de la ville de Paris</b> ; <b>Plan de la ville de Paris (1846)</b> ; etc."
        },
        "reference_url": {
            "validators": [is_valid_url],
            "label": "URL de référence",
            "description": "URL de référence de l'image (point d'accès à la ressource). Sinon laisser la valeur <b>'unknown_url'</b> par défaut. "
                           "Exemple : <b>http://gallica.bnf.fr/ark:/12148/btv1b9005061j</b> ou <b>	http://gallica.bnf.fr/ark:/12148/btv1b90055989/f1.item</b> ; etc."
        },
        "iiif_url": {
            "validators": [is_valid_url],
            "label": "URL IIIF",
            "description": "URL IIIF de l'image. "
                           "Exemple : <b>https://gallica.bnf.fr/iiif/ark:/12148/btv1b90055989/f1/full/1000,/0/native.jpg	</b> ; etc."
        }
    }


    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        "img_name": ImageUploadField(
            "Charger une image", base_path=settings.IMAGE_STORE,
            thumbnail_size=False,
            endpoint="static",
            url_relative_path="/images_store/",
            allowed_extensions=['jpg', 'jpeg', 'png'],
            namegen=prefix_name
        )
    }

    def on_model_change(self, form, model, is_created):
        # display form data
        data = form.data
        if data['img_name'] is None:
            model.img_name = "unknown.jpg"





class PatentHasRelationsView(GlobalModelView):
    column_list = [
        "id",
        "_id_dil",
        "person_id",
        "person_related_id",
        "patent_id",
        "type",
        "created_at",
        "updated_at",
        "last_editor"
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "person_id": "Imprimeur",
        "person_related_id": "Imprimeur lié",
        "patent_id": "Brevet",
        "type": "Type de relation",
        "created_at": "Créé le",
    }

    column_formatters = {
        'person_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("person.details_view", id=m.person_id)}">'
                f'{m.person_id}</a>'
            ) if m.person else "(Aucune personne)"),
        'person_related_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("person.details_view", id=m.person_related_id)}">'
                f'{m.person_related_id}</a>'
            ) if m.person_related else "(Aucune personne)"),
        'patent_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("patent.details_view", id=m.patent_id)}">'
                f'{m.patent_id}</a>'
            ) if m.patent else "(Aucun brevet)"),
        'type': lambda v, c, m, p: (
            Markup(
                f'<span>{m.type}</span>'
            ) if m.type else "(Aucun type)"),
    }


class AddressView(GlobalModelView):
    column_list = [
        "id",
        "_id_dil",
        "label",
        "city_label",
        "city_id",
        "created_at",
        "updated_at",
        "last_editor"
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "label": "Libellé",
        "city_label": "Ville",
        "city_id": "Ville (référentiel)",
        "created_at": "Créé le",
        "updated_at": "Modifié le",
        "last_editor": "Dernier éditeur"
    }

    column_formatters = {
        'city_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("city.details_view", id=m.city_id)}">'
                f'{m.city}</a>'
            ) if m.city_label else "(Aucune ville)"
        )
    }

    """
    label = Column(String, nullable=False, unique=False, default='inconnue')
    city_label = Column(String, nullable=False, unique=False, default=None)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True, unique=False, default=None)
    """

    form_columns = [
        "label",
        "city_label",
        "city_id"
    ]

    form_args = {
        "label": {
            "label": "Libellé de l'adresse",
            "description": "Libellé de l'adresse. "
                           "Exemple : <b>1, rue de la Paix</b> ; <b>2, rue du Faubourg Saint-Honoré</b> ; etc. Laisser <b>'inconnue'</b> si l'adresse est inconnue."
        },
        "city_label": {
            "label": "Ville",
            "description": "Libellé de la ville de l'adresse. Il peut correspondre au toponyme ancien. "
                           "Exemple : <b>Paris</b> ; <b>Lyon</b> ; <b>Abergement-Clémenciat (L')</b> etc.",
        },
        "city_id": {
            "label": "Ville (référentiel)",
            "description": "Ville de l'adresse dans le référentiel."
        }
    }

    form_ajax_refs = {
        'city_id': QueryAjaxModelLoader(
            'city_id', session, City, fields=['label'], page_size=10,
            placeholder='Commencer la saisie puis sélectionner une ville...',
            allow_blank=True
        )
    }



class PatentView(GlobalModelView):
    column_list = [
        "id",
        "_id_dil",
        "drupal_nid",
        "person_id",
        "date_start",
        "date_end",
        "references",
        "comment",
        "city_label",
        "city_id",
        "created_at",
        "updated_at",
        "last_editor"
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "drupal_nid": "ancien ID Drupal",
        "person_id": "Imprimeur concerné",
        "date_start": "Date de début",
        "date_end": "Date de fin",
        "references": "Bibliographie / Sources",
        "comment": "Remarques",
        "city_label": "Ville du brevet",
        "city_id": "Ville du brevet (référentiel)",
        "created_at": "Créé le",
        "updated_at": "Modifié le",
        "last_editor": "Dernier éditeur"
    }

    column_formatters = {
        'city_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("city.details_view", id=m.city_id)}">'
                f'{m.city}</a>'
            ) if m.city_label else "(Aucune ville)"),
        'person_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("person.details_view", id=m.person_id)}">'
                f'{m.person_id}</a>'
            ) if m.person else "(Aucun imprimeur)"),
    }


class CityView(GlobalModelView):
    column_searchable_list = ["label"]
    # Transformer la colonne `long_lat` pour afficher une carte
    column_formatters = {
        'long_lat': lambda v, c, m, p: (
            Markup(f'''
            <div id="map-{m.id}" style="height: 200px; width: 300px; margin: auto;"></div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    var raw_coords = "{m.long_lat}";

                    try {{
                        var coords = JSON.parse(raw_coords.replace("(", "[").replace(")", "]"));
                        // invert item 0 and 1 in the list
                        coords = [coords[1], coords[0]];
                        if (coords && coords.length === 2) {{
                            var map = L.map("map-{m.id}").setView(coords, 13);
                            L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                                maxZoom: 19,
                                attribution: '© OpenStreetMap contributors'
                            }}).addTo(map);
                            L.marker(coords).addTo(map).bindPopup('Coordonnées : ' + coords).openPopup();
                        }}
                    }} catch (e) {{
                        console.error("Erreur de parsing des coordonnées : ", e);
                    }}
                }});
            </script>
        ''') if m.long_lat else "(Pas de coordonnées disponibles)")
    }

    form_columns = [
        "label",
        "country_iso_code",
        "long_lat",
        "insee_fr_code",
        "insee_fr_department_code",
        "insee_fr_department_label",
        "geoname_id",
        "wikidata_item_id",
        "dicotopo_item_id",
        "databnf_ark",
        "viaf_id",
        "siaf_id"
    ]

    form_args = {
        "label": {
            "label": "Libellé de la ville",
            "description": "Libellé de la ville. "
                           "Exemple : <b>Paris</b> ; <b>Lyon</b> ; <b>Abergement-Clémenciat (L')</b> etc."
        },
        "country_iso_code": {
            "label": "Code ISO du pays",
            "description": "Code ISO 3166 du pays de la ville. "
                           "Exemple : <b>FR</b> pour la France ; <b>BE</b> pour la Belgique ; etc."
        },
        "long_lat": {
            "label": "Coordonnées géographiques (longitude, latitude)",
            "description": "Coordonnées géographiques de la ville (longitude, latitude). "
        },
        "insee_fr_code": {
            "label": "Code de la ville (INSEE)",
            "description": "Code géographique officiel de l'INSEE pour la ville. "
                           "Exemple : <b><a href='https://www.insee.fr/fr/metadonnees/geographie/commune/01001-labergement-clemenciat' target='_blank'>01001</a></b> pour Abergement-Clémenciat (L')."
        },
        "insee_fr_department_code": {
            "label": "Code du département (INSEE)",
            "description": "Code géographique officiel de l'INSEE pour le département de la ville. "
                           "Exemple : <b>DEP_75</b> pour Paris ; <b>DEP_69</b> pour Lyon ; etc."
        },
        "insee_fr_department_label": {
            "label": "Libellé du département (INSEE)",
            "description": "Libellé du département INSEE. "
                           "Exemple : <b>Paris</b> pour Paris ; <b>Rhône</b> pour Lyon ; etc."
        },
        "geoname_id": {
            "label": "Identifiant Geonames",
            "description": "ID Geonames de la ville. "
                           "Exemple : <a href='https://www.geonames.org/2988507/paris.html' target='_blank'><b>2988507</b></a> pour Paris."
        },
        "wikidata_item_id": {
            "label": "Identifiant Wikidata",
            "description": "QID Wikidata de la ville. "
                           "Exemple : <a href='https://www.wikidata.org/wiki/Q456' target='_blank'><b>Q456</b></a> pour Lyon."
        },
        "dicotopo_item_id": {
            "label": "Identifiant Dicotopo (ENC)",
            "description": "ID Dicotopo de la ville. "
                           "Exemple : <a href='https://dicotopo.cths.fr/places/P17270150' target='_blank'><b>P17270150</b></a> pour Courcelles."
        },
        "databnf_ark": {
            "label": "ARK BNF",
            "description": "ARK BNF (catalogue général) de la ville. "
                           "Exemple : <a href='https://catalogue.bnf.fr/ark:/12148/cb15272211b' target='_blank'><b>ark:/12148/cb15272211b</b></a> pour Lyon."
        },
        "viaf_id": {
            "label": "Identifiant VIAF",
            "description": "ID VIAF de la ville. "
                           "Exemple : <a href='https://viaf.org/fr/viaf/312739984' target='_blank'><b>131453</b></a> pour Rennes."
        },
        "siaf_id": {
            "label": "Identifiant SIAF",
            "description": "ID SIAF de la ville. "
                           "Exemple : <a href='https://francearchives.gouv.fr/fr/location/217180640'><b>217180640</b></a> pour Port-Sainte-Marie (Lot-et-Garonne, France)."
        }
    }


class PatentHasRelationsView(GlobalModelView):
    column_list = [
        "id",
        "_id_dil",
        "person_id",
        "person_related_id",
        "patent_id",
        "type",
        "created_at",
        "updated_at",
        "last_editor"
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "person_id": "Imprimeur",
        "person_related_id": "Imprimeur lié",
        "patent_id": "Brevet",
        "type": "Type de relation",
        "created_at": "Créé le",
    }

    column_formatters = {
        'person_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("person.details_view", id=m.person_id)}">'
                f'{m.person_id}</a>'
            ) if m.person else "(Aucune personne)"),
        'person_related_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("person.details_view", id=m.person_related_id)}">'
                f'{m.person_related_id}</a>'
            ) if m.person_related else "(Aucune personne)"),
        'patent_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("patent.details_view", id=m.patent_id)}">'
                f'{m.patent_id}</a>'
            ) if m.patent else "(Aucun brevet)"),
        'type': lambda v, c, m, p: (
            Markup(
                f'<span>{m.type}</span>'
            ) if m.type else "(Aucun type)"),
    }


class PatentHasImagesView(GlobalModelView):
    column_list = [
        "id",
        "_id_dil",
        "patent_id",
        "image_id",
        "created_at",
        "updated_at",
        "last_editor"
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "patent_id": "Brevet",
        "image_id": "Image",
        "created_at": "Créé le",
        "updated_at": "Modifié le",
        "last_editor": "Dernier éditeur"
    }

    column_formatters = {
        'patent_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("patent.details_view", id=m.patent_id)}">'
                f'{m.patent_id}</a>'
            ) if m.patent_images else "(Aucun brevet)"),
        'image_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("image.details_view", id=m.image_id)}">'
                f'{m.image_id}</a>'
            ) if m.image_patents else "(Aucune image)"),
    }


"""
class PatentHasAddressesView(GlobalModelView):
    column_list = [
        "id",
        "_id_dil",
        "person_id",
        "address_id",
        "date_occupation",
        "created_at",
        "updated_at",
        "last_editor"
    ]
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "person_id": "Imprimeur",
        "address_id": "Adresse",
        "date_occupation": "Date d'occupation",
        "created_at": "Créé le",
        "updated_at": "Modifié le",
        "last_editor": "Dernier éditeur"
    }

    column_formatters = {
        'patent_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("patent.details_view", id=m.patent_id)}">'
                f'{m.patent_id}</a>'
            ) if m.patent else "(Aucun brevet)"),
        'address_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("address.details_view", id=m.address_id)}">'
                f'{m.address_id}</a>'
            ) if m.address else "(Aucune adresse)"),
    }
"""
