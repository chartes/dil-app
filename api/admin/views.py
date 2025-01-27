"""
"""

import json

from flask import url_for, jsonify, request
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Field
from markupsafe import Markup

from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask_admin.model.fields import AjaxSelectField
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from flask_admin.form.widgets import Select2Widget
from flask_admin.model.widgets import AjaxSelect2Widget
from flask_admin import expose
from flask_admin.model.form import InlineFormAdmin
from sqlalchemy import or_

from wtforms import Form
from wtforms import SelectField
from wtforms.fields import StringField, FieldList

from .validators import (is_valid_date)
from ..models import *
from wtforms import TextAreaField
from wtforms.widgets import TextArea

from .widget import QuillWidget
from flask_admin.form.widgets import Select2Widget
from flask_admin.model.form import InlineFormAdmin

from collections import defaultdict
from werkzeug.datastructures import ImmutableMultiDict

from .formaters import _format_label_form_with_tooltip


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


class ImageView(GlobalModelView):
    """View for the image model."""
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
            f'<img src="{url_for("static", filename=f"img/images/{m.img_name}")}" '
            'style="max-width: 200px; max-height: 200px;">'
            if m.img_name else '<p>Pas d\'image</p>'
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


class PrinterView(GlobalModelView):
    """View for the person model."""
    edit_template = 'admin/edit.html'
    create_template = 'admin/edit.html'
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
                     "person_addresses": "Adresses personnelles",
                     "patents": "Brevets",
                     "created_at": "Créé le",
                     "updated_at": "Modifié le",
                     "last_editor": "Dernier éditeur",
                     'birth_cities': "Ville de naissance (référentiel)",
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
                f'{m.birth_cities}</a>'
            ) if m.birth_cities else "(Aucune ville)"
        )
    }

    inline_models = [
        (PersonHasAddresses, {
            "form_columns": ["id",
                             "address",
                             "date_occupation"],
            "column_labels": {
                "address": "Adresse",
                "date_occupation": "Date d'occupation",
            },
            "form_args": {
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
                "address": QueryAjaxModelLoader(
                    "address", session, Address, fields=["label"], page_size=10,
                    placeholder="Indiquer l'adresse dans le référentiel...",
                    allow_blank=True
                )
            }
        }),

        (Patent, {
            "form_columns": ["id",
                             "date_start",
                             "date_end",
                             "city_label",
                             "city",
                             "references",
                             "comment",
                             "addresses",
                             "relation_container",
                             "patent_images",
                             ],
            "column_labels": {
                "date_start": "Début",
                "date_end": "Fin",
                "city_label": "Ville",
                "city": "Ville (référentiel)",
                "references": "Bibliographie / Sources",
                "comment": "Mémo (édition)",
                "addresses": "Addresses professionnelles",
                "patent_images": "Images"

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
                "patent_images": {"onchange": "addPreview(this);", "class": "select2-image"},
                "relation_container": {"onchange": "makeRelation(this)", "class": "relation-container-attach"}
            },
            "form_ajax_refs": {
                "city": QueryAjaxModelLoader(
                    "city", session, City, fields=["label"], page_size=10,
                    placeholder="Indiquer la ville dans le référentiel...",
                    allow_blank=True
                ),
                "addresses": QueryAjaxModelLoader(
                    "addresses", session, Address, fields=["label"], page_size=10,
                    placeholder="Indiquer une ou plusieurs adresses..",
                    allow_blank=True
                ),
                "patent_images": ImageAjaxModelLoader(
                    "patent_images", session, Image, fields=["label"], page_size=10,
                    placeholder="Lier des images au brevet...",
                    allow_blank=True,
                )
            },

        }),

    ]

    # Form attributes

    form_columns = [
        "lastname",
        "firstnames",
        "birth_date",
        "birth_city_label",
        "birth_cities",
        "personal_information",
        "professional_information",
        "comment"
    ]

    # Define form widget arguments
    form_widget_args = {
        "firstnames": {
            "class": "input-select-tag-form-1 form-control",
        },
    }

    #
    form_excluded_columns = ('id', '_id_dil', 'created_at', 'updated_at', 'last_editor')

    # form_ajax_refs = {
    #    'birth_city_id': CityAjaxModelLoader('birth_city_id')
    # }

    form_ajax_refs = {
        'birth_cities': QueryAjaxModelLoader(
            'birth_cities', session, City, fields=['label'], page_size=10,
            placeholder='Indiquer la ville de naissance dans le référentiel...',
            allow_blank=True
        )
    }

    form_args = {
        "lastname": {
            "label": _format_label_form_with_tooltip(label="Nom",
                                                     comment="Nom de l'imprimeur.")
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
        },

    }

    @expose('/get_image_details/', methods=['GET', 'POST'])
    def get_image_details(self):
        if request.method in ['GET', 'POST']:
            image_id = request.args.get('id')  # Récupère l'ID de l'image depuis les paramètres GET
            if not image_id:
                return jsonify({'error': 'No ID provided'}), 400

            # Cherchez l'image dans la base
            image = session.query(Image).filter_by(id=image_id).first()
            if not image:
                return jsonify({'error': 'Image not found'}), 404

            # Retourner les détails de l'image
            img_name = image.img_name
            if (image.img_name is None):
                img_name = image.iiif_url
            return jsonify({
                'id': image.id,
                'label': image.label,
                'img_name': image.img_name,
                'img_url': url_for("static", filename=f"img/images/{img_name}") if image.img_name else img_name
            })

    @expose('/get_printers', methods=['GET'])
    def ajax_printers(self):
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
        # Récupère les relations de brevet pour l'imprimeur spécifié
        relations = (
            session.query(PatentHasRelations)
            .filter(PatentHasRelations.person_id == person_id)
            .all()
        )

        # Grouper les relations par `patent_id`
        grouped_relations = {}
        for relation in relations:
            if relation.patent_id not in grouped_relations:
                grouped_relations[relation.patent_id] = []
            grouped_relations[relation.patent_id].append({
                "person_related_id": relation.person_related_id,
                "relation_type": relation.type.value,  # Convertir Enum en chaîne
            })

        # Réindexer les groupes en partant de zéro
        result = {str(index): grouped_relations[patent_id] for index, patent_id in enumerate(grouped_relations)}

        return jsonify(result)

    """
    def update_model(self, form, model):
        #print(form)
        #for field_name, field in form._fields.items():
        #    print(f"Champ: {field_name}, Valeur: {field.data}")
        #print(request.form.to_dict(flat=False))
        pass

    def on_model_change(self, form, model, is_created):
        #print(form)
        #print(request.form)
        pass

    def after_model_change(self, form, model, is_created):
        
        # on ajoute les relations entre brevets une fois le modèle update
        if is_created:
            print('nouveau modèle sauvegardé')
        print(form)
        print(request.form)
        data_dict = request.form.to_dict(flat=False)
        print(data_dict)
        grouped_data = defaultdict(lambda: {"printers": [], "relation_types": []})
        for key, values in data_dict.items():
            if key.startswith('dynamic_printers'):
                index = key.split('[')[1].split(']')[0]  # Extraire l'index
                grouped_data[index]['printers'].extend(values)
            elif key.startswith('dynamic_relation_types'):
                index = key.split('[')[1].split(']')[0]  # Extraire l'index
                grouped_data[index]['relation_types'].extend(values)
        # Convertir en un format standard
        patents_relations = {k: v for k, v in grouped_data.items()}

        print(patents_relations)
        
        pass
"""

    # def get_list_columns(self):
    #    """Return list of columns to display in list view."""
    #    return super(PrinterView, self).get_list_columns()

    # def get_list_form(self):
    #    """Return list of columns to display in list form."""
    #    return super(PrinterView, self).get_list_form()


class CityView(GlobalModelView):
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
            ) if m.patent else "(Aucun brevet)"),
        'image_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("image.details_view", id=m.image_id)}">'
                f'{m.image_id}</a>'
            ) if m.image else "(Aucune image)"),
    }


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
