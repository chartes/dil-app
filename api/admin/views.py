"""
views.py

Model views for the admin interface.
"""
from unidecode import unidecode

from flask import (url_for,
                   jsonify,
                   request,
                   redirect,
                   flash)
from flask_admin.contrib.sqla import ModelView
from flask_admin import (expose,
                         AdminIndexView,
                         BaseView)
from flask_admin.form import ImageUploadField
from flask_login import (current_user,
                         logout_user,
                         login_user)

from wtforms.fields import StringField, PasswordField
from wtforms import BooleanField
from wtforms.widgets import TextArea

from markupsafe import Markup
from sqlalchemy import or_

from .validators import (is_valid_date,
                         is_valid_url,
                         is_only_digits,
                         is_wikidata_qid,
                         is_ark_id,
                         validate_coordinates,
                         validate_address)
from ..models.models import (
    User,
    Person,
    City,
    Address,
    Patent,
    Image,
    PersonHasAddresses,
    PatentHasAddresses,
    PatentHasImages,
    PatentHasRelations,
    type_patent_relations
)
from .forms import LoginForm
from .widget import QuillWidget

from .formaters import (_format_label_form_with_tooltip,
                        _format_link_add_model,
                        _format_href)
from .model_handler import PrinterModelChangeHandler

from api.config import settings
from api.crud import (get_user,
                      get_address,
                      get_patents,
                      get_printer)
from api.database import session
from api.admin.views_dir.utils import *
from api.admin.views_dir.loaders import *

EDIT_ENDPOINTS = ["person", "city", "address", "image"]
can_edit_roles = ['ADMIN', 'EDITOR', 'CONTRIBUTOR']
can_delete_roles = ['ADMIN', 'EDITOR']
can_create_roles = ['ADMIN', 'EDITOR', 'CONTRIBUTOR']

BASE_PREFIX_ADD_MODEL = '/dil-db/dil-db/admin/'

version_metadata = {
    "created_at": "Date de création",
    "updated_at": "Date de modification",
    "last_editor": "Dernier éditeur"
}


class AdminView(AdminIndexView):
    """Custom view for administration."""

    @expose('/login', methods=('GET', 'POST'))
    def login(self):
        """Login view."""
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = get_user(session, dict(username=form.username.data))
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f'Vous êtes connecté en tant que {current_user.username} !', 'success')
                return redirect(url_for('admin.index'))
            else:
                flash('Identifiant ou mot de passe incorrect !', 'danger')
                return self.render('admin/login.html', form=form)
        return self.render('admin/login.html', form=form)

    @expose('/logout', methods=('GET', 'POST'))
    def logout(self):
        """Logout view."""
        logout_user()
        flash('Vous êtes déconnecté !', 'warning')
        return redirect(url_for('admin.index'))


class GlobalModelView(ModelView):
    """Global & Shared parameters for the model views."""
    column_display_pk = True
    can_view_details = True
    can_set_page_size = False
    action_disallowed_list = ['delete']
    list_template = 'admin/list.html'

    # list_template = 'admin/list.html'
    def is_accessible(self):
        if current_user.is_authenticated:
            self.can_edit = current_user.role in can_edit_roles
            self.can_delete = current_user.role in can_delete_roles
            self.can_create = current_user.role in can_create_roles
        else:
            self.can_edit = False
            self.can_delete = False
            self.can_create = False
        self.can_export = True
        return True






class UserView(ModelView):
    edit_template = 'admin/edit.user.html'
    create_template = 'admin/edit.user.html'
    list_template = 'admin/list.user.html'
    column_list = ["id",
                   "username",
                   "email",
                   "role",
                   "created_at",
                   "updated_at"]
    column_labels = {
        "id": "ID",
        "username": "Nom d'utilisateur",
        "role": "Rôle",
        "email": "Adresse email",
        "created_at": "Créé le",
        "updated_at": "Modifié le"
    }
    column_searchable_list = ["username", "email"]
    # hide the password hash in edit/create form
    form_excluded_columns = ["password_hash",
                             "created_at",
                             "updated_at"]

    form_columns = ["username",
                    "email",
                    "role",
                    "new_password"]

    form_extra_fields = {
        "new_password": PasswordField("Nouveau mot de passe",
                                      id="new_password_field"),

    }

    @expose("/generate_password/", methods=["GET", "POST"])
    def new_password(self):
        if request.method in ["GET", "POST"]:
            password = User.generate_password()

            return jsonify({"password": password}), 200
        return jsonify({"error": "No password provided"}), 400

    def on_model_change(self, form, model, is_created):
        if form.new_password.data:
            if model.id == 1:
                if current_user.id != 1:
                    flash("Vous ne pouvez pas modifier le mot de passe de ce compte administrateur.", "danger")
                else:

                    model.set_password(form.new_password.data)
                    session.commit()
                    return model
            else:
                model.set_password(form.new_password.data)
                session.commit()
                return model

        if is_created:
            model.set_password(form.new_password.data)
            session.commit()
            return model

    def delete_model(self, model):
        if model.id == current_user.id:
            flash("Vous ne pouvez pas supprimer votre propre compte.", "danger")
            return False
        if model.id == 1:
            flash("Vous ne pouvez pas supprimer ce compte administrateur.", "danger")
            return False
        if model.role == "Admin":
            if current_user.role != "ADMIN":
                flash("Vous ne pouvez pas supprimer un compte administrateur.", "danger")
                return False

        return super().delete_model(model)

    def is_accessible(self):
        access_view = ['ADMIN']
        if current_user.is_authenticated:
            return current_user.role in access_view
        else:
            return False


class PrinterView(GlobalModelView):
    """View for the person model."""
    edit_template = 'admin/edit.printer.html'
    create_template = 'admin/edit.printer.html'
    list_template = "admin/list.printer.html"
    details_template = "admin/details.printer.html"
    column_auto_select_related = True

    column_list = ["id",
                   '_id_dil',
                   "lastname",
                   "firstnames",
                   "birth_date",
                   "birth_city_label",
                   "birth_city_id",
                   # "personal_information",
                   # "professional_information",
                   "comment"] + list(version_metadata.keys())

    column_details_list = [
        "lastname",
        "firstnames",
        "birth_date",
        "birth_city_label",
        "city",
        "personal_information",
        "professional_information",
    ]

    column_formatters_detail = {
        "personal_information": lambda v, c, m, p: Markup(
            m.personal_information) if m.personal_information else "Aucune information personnelle disponible.",
        "professional_information": lambda v, c, m, p: Markup(
            m.professional_information) if m.professional_information else "Aucune information professionnelle disponible.",
    }

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
                     **version_metadata
                     }
    column_searchable_list = ["lastname",
                              "firstnames",
                              # "birth_city_label",
                              # "personal_information",
                              # "professional_information"
                              ]
    column_filters = ["lastname",
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
                                                          href=f'{BASE_PREFIX_ADD_MODEL}address/new/?url={BASE_PREFIX_ADD_MODEL}address/')
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
                "address_persons": GenericAjaxModelLoader(
                    "address_persons",
                    session,
                    Address,
                    search_field="label",
                    page_size=10,
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
                "addresses_container",
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
                # place for inner form fields. These placeholder container are hidden in the form.
                # They are used as a anchor for the js to attach the form fields.
                "relation_container": StringField(
                    label="Relations avec imprimeurs",
                    widget=TextArea(),
                    render_kw={"id": "relation-container"}
                ),
                "addresses_container": StringField(
                    label="Adresses professionnelles",
                    widget=TextArea(),
                    render_kw={"id": "addresses-container"}
                ),
            },
            "form_widget_args": {
                "images": {"onchange": "addPreview(this);", "class": "select2-image"},
                # These containers are hidden in the form and used as anchor for the js to attach the form fields.
                "addresses_container": {"onchange": "makeAddress(this)", "class": "addresses-container-attach"},
                "relation_container": {"onchange": "makeRelation(this)", "class": "relation-container-attach"}
            },
            "form_ajax_refs": {
                "city": GenericAjaxModelLoader(
                    "city",
                    session,
                    City,
                    search_field="label",
                    page_size=10,
                    placeholder="Commencer la saisie puis sélectionner une ville...",
                    allow_blank=True
                ),
                "images": GenericAjaxModelLoader(
                    "images",
                    session,
                    Image,
                    search_field="label",
                    page_size=10,
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
                    "description": "Exemples : Verdun-sur-le-Doubs (Saône-et-Loire) ; "
                                   "Clermont-Ferrand (Puy-de-Dôme) ; Paris etc."
                },
                "city": {
                    "label": _format_label_form_with_tooltip(label="Ville (référentiel)",
                                                             comment="Ville du brevet dans le référentiel."),
                    "description": _format_link_add_model(description="une nouvelle ville",
                                                          href=f'{BASE_PREFIX_ADD_MODEL}city/new/?url={BASE_PREFIX_ADD_MODEL}city/')
                },
                "images": {
                    "label": _format_label_form_with_tooltip(label="Images",
                                                             comment="Images liées au brevet."),
                    "description": _format_link_add_model(description="une nouvelle image",
                                                          href=f'{BASE_PREFIX_ADD_MODEL}image/new/?url={BASE_PREFIX_ADD_MODEL}image/')
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
        'city': GenericAjaxModelLoader(
            'city',
            session,
            City,
            search_field="label",
            page_size=10,
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
                                                  href=f'{BASE_PREFIX_ADD_MODEL}city/new/?url={BASE_PREFIX_ADD_MODEL}city/')
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
            "description": "Exemples : Verdun-sur-le-Doubs (Saône-et-Loire) ; Clermont-Ferrand (Puy-de-Dôme) ; Paris etc."
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

        model.last_editor = current_user.username
        session.commit()

    def get_list_columns(self):
        """Return list of columns to display in list view."""
        return super(PrinterView, self).get_list_columns()

    def get_list_form(self):
        """Return list of columns to display in list form."""
        return super(PrinterView, self).get_list_form()

    def render(self, template, **kwargs):
        """Render a template with the given context."""
        if template == "admin/details.printer.html":
            printer = get_printer(session, {
                'id': kwargs['model'].id
            })
            patents = get_patents(session, {
                'person_id': kwargs['model'].id
            })

            # Tri sécurisé sur les addresses_relations
            for patent in patents:
                if hasattr(patent, 'addresses_relations') and patent.addresses_relations:
                    patent.addresses_relations = sorted(
                        patent.addresses_relations,
                        key=lambda a: a.date_occupation or ""
                    )

            id_patents = [evt.id for evt in get_printer(session, {'id': kwargs['model'].id}).patents]
            if len(patents) == len(id_patents):
                return super(PrinterView, self).render(template, **kwargs, patents=list(zip(id_patents, patents)),
                                                       printer=printer)
            else:
                return super(PrinterView, self).render(template, **kwargs)
        return super(PrinterView, self).render(template, **kwargs)

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        query = self.session.query(self.model)
        all_rows = query.all()

        if search:
            normalized_search = unidecode(search).lower().strip()
            search_tokens = normalized_search.split()

            def match(row):
                combined = f"{row.lastname or ''} {row.firstnames or ''}"
                normalized_combined = unidecode(combined).lower()
                return all(token in normalized_combined for token in search_tokens)

            filtered_rows = list(filter(match, all_rows))
        else:
            filtered_rows = all_rows

        count = len(filtered_rows)

        # Tri optionnel
        if sort_field:
            reverse = sort_desc
            filtered_rows.sort(
                key=lambda x: getattr(x, sort_field, '').lower() if getattr(x, sort_field) else '',
                reverse=reverse
            )

        # Pagination Python
        if page_size:
            start = page * page_size
            end = start + page_size
            filtered_rows = filtered_rows[start:end]

        return count, filtered_rows

    # Expose custom routes for printer view
    # for Ajax requests

    @expose('/get_image_details/', methods=['GET', 'POST'])
    def get_image_details(self):
        """Retrieves details of an image from the database"""
        if request.method in ['GET', 'POST']:
            image_id = request.args.get('id')  # Récupère l'ID de l'image depuis les paramètres GET
            patent_id = request.args.get('patent_id')  # Récupère l'ID du brevet depuis les paramètres GET
            if not image_id:
                return jsonify({'error': 'This patent has no image.'}), 200
            image = session.query(Image).filter_by(id=image_id).first()
            try:
                is_pinned = session.query(PatentHasImages).filter_by(image_id=image_id,
                                                                     patent_id=patent_id).first().is_pinned
            except AttributeError:
                is_pinned = False

            if not image:
                return jsonify({'error': 'This image no exist.'}), 200

            img_name = image.img_name
            return jsonify({
                'id': image.id,
                'label': image.label,
                'img_name': image.img_name,
                'img_url': url_for("static", filename=f"images_store/{img_name}") if (img_name != "unknown.jpg") or (
                        image.iiif_url is not None) else url_for("static", filename="icons/preview-na.png"),
                'img_iiif_url': image.iiif_url,
                'is_pinned': is_pinned,
                'fallback_url': url_for("static", filename="icons/preview-na.png"),
                'fallback_iiif_url': url_for("static", filename="icons/preview-na-iiif.png")
            })

    @expose('/get_printers', methods=['GET'])
    def ajax_printers(self):
        """Retrieves a list of printers for Select2."""
        search = request.args.get('q', '')
        query = (
            session.query(Person)
            .filter(
                or_(
                    Person.lastname.ilike(f"%{search.lower()}%"),
                    Person.firstnames.ilike(f"%{search.lower()}%")
                )
            )
            .order_by(Person.lastname, Person.firstnames)
        ).limit(20)

        results = [{"id": person.id, "text": repr(person)} for person in query]
        return jsonify(results)

    @expose('/get_addresses', methods=['GET'])
    def ajax_addresses(self):
        """Retrieves a list of addresses for Select2."""
        search = request.args.get('q', '')  # Récupère le terme de recherche
        query = (
            session.query(Address)
            .filter(Address.label.ilike(f"%{search.lower()}%"))
        ).limit(20)  # Limiter les résultats

        results = [{"id": address.id, "text": repr(address)} for address in query]
        return jsonify(results)

    @expose('/get_printer/<int:person_id>', methods=['GET'])
    def ajax_printer(self, person_id):
        """Retrieves details of a printer from the database."""
        person = get_printer(session, {
            'id': person_id
        })
        return jsonify({
            "id": person_id,
            "text": repr(person)
        })

    @expose('/get_address/<int:address_id>', methods=['GET'])
    def ajax_address(self, address_id):
        """Retrieves details of a printer from the database."""
        address = get_address(session, {
            'id': address_id
        })
        return jsonify({
            "id": address_id,
            "text": repr(address)
        })

    @expose('/get_patent_relations/<int:person_id>', methods=['GET'])
    def get_patent_relations(self, person_id):
        """Retrieves relations for a printer."""
        patents = session.query(Patent).filter_by(person_id=person_id).all()
        patents_id = [p.id for p in patents]
        grouped_relations = {}
        for pid in patents_id:
            relations = (
                session.query(PatentHasRelations)
                .filter(PatentHasRelations.person_id == person_id, PatentHasRelations.patent_id == pid)
                .all()
            )
            if pid not in grouped_relations:
                grouped_relations[pid] = []
            for relation in relations:
                relation_type = [k for k, v in type_patent_relations.items() if v == relation.type][0]
                grouped_relations[pid].append({
                    "id": relation.person_related_id,
                    "data": relation_type
                })


        return jsonify(grouped_relations)

    @expose('/get_pro_addresses/<int:person_id>', methods=['GET'])
    def get_pro_addresses(self, person_id):
        """Retrieves professional addresses for a printer."""
        patents = session.query(Patent).filter_by(person_id=person_id).all()
        patents_id = [p.id for p in patents]
        grouped_addresses = {}
        for pid in patents_id:
            addresses = (
                session.query(PatentHasAddresses)
                .filter(PatentHasAddresses.patent_id == pid)
                .all()
            )
            if pid not in grouped_addresses:
                grouped_addresses[pid] = []
            for address in addresses:
                grouped_addresses[pid].append({
                    "id": address.address_id,
                    "data": address.date_occupation
                })

        return jsonify(grouped_addresses)


class ImageView(GlobalModelView):
    """View for the image model."""
    edit_template = "admin/edit.image.html"
    create_template = "admin/edit.image.html"
    column_list = ["id",
                   "_id_dil",
                   "label",
                   "img_name",
                   "reference_url",
                   "iiif_url",
                   ] + list(version_metadata.keys())
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "label": "Libellé",
        "img_name": "Image",
        "reference_url": "URL de référence (opt.)",
        "iiif_url": "URL IIIF (opt.)",
        **version_metadata}

    column_searchable_list = ["label"]

    column_formatters = {
        'img_name': lambda v, c, m, p: Markup(
            f'<img src="{url_for("static", filename=f"images_store/{m.img_name}")}" '
            'style="max-width: 200px; max-height: 200px;">'
            if m.img_name != 'unknown.jpg' else f'<img src="{m.iiif_url}" style="max-width: 200px; max-height: 200px;">'
        ),
        # 'reference_url': lambda v, c, m, p: Markup(
        #    f'<a href="{m.reference_url}" target="_blank">{m.reference_url}</a>'
        #    if m.reference_url else '<p>Pas d\'URL de référence</p>'
        # ),
        'reference_url': lambda v, c, m, p: _format_href(prefix_url="",
                                                         label=m.reference_url) if m.reference_url != 'unknown_url' else 'Inconnue',
        'iiif_url': lambda v, c, m, p: _format_href(prefix_url="", label=m.iiif_url) if m.iiif_url else 'Inconnue'
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
        data = form.data
        if data['img_name'] is None:
            model.img_name = "unknown.jpg"

        model.last_editor = current_user.username
        session.commit()


class PatentHasRelationsView(GlobalModelView):
    column_list = [
                      "id",
                      "_id_dil",
                      "person_id",
                      "person_related_id",
                      "patent_id",
                      "type",
                  ] + list(version_metadata.keys())
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "person_id": "Imprimeur",
        "person_related_id": "Imprimeur lié",
        "patent_id": "Brevet",
        "type": "Type de relation",
        **version_metadata
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
    column_list = ["id",
                   "_id_dil",
                   "label",
                   "city_label",
                   "city_id",
                   ] + list(version_metadata.keys())
    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "label": "Libellé",
        "city_label": "Ville",
        "city_id": "Ville (référentiel)",
        **version_metadata
    }

    column_searchable_list = ["label", "city_label"]

    column_formatters = {
        'city_id': lambda v, c, m, p: (
            Markup(
                f'<a href="{url_for("city.details_view", id=m.city_id)}">'
                f'{m.city}</a>'
            ) if m.city_label else "(Aucune ville)"
        )
    }

    form_columns = [
        "not_french_address",
        "label",
        "city_label",
        "city"
    ]

    form_args = {
        "label": {
            "validators": [validate_address],
            "label": "Libellé de l'adresse",
            "description": "Libellé de l'adresse. "
                           "Exemple : <b>1, rue de la Paix</b> ; <b>2, rue du Faubourg Saint-Honoré</b> ; <b>12 quinquies, rue Victor Hugo</b> ; <b>3 ter, avenue des Champs-Élysées</b> ; <b>rue de la Paix</b> ; <b>inconnue</b> ; <b>200 West 45th Street</b> (adresse hors france) etc."
                           "; etc. Laisser <b>'inconnue'</b> si l'adresse est inconnue."
        },
        "city_label": {
            "label": "Ville",
            "description": "Libellé de la ville de l'adresse. Il peut correspondre au toponyme ancien. "
                           "Exemple : <b>Paris</b> ; <b>Lyon</b> ; <b>Abergement-Clémenciat (L')</b> etc.",
        },
        "city": {
            "label": "Ville (référentiel)",
            "description": "Ville de l'adresse dans le référentiel."
        },
        "is_french": {
            "label": "Adresse française",
            "description": "Cocher si l'adresse est française."
        }
    }

    form_ajax_refs = {
        'city': GenericAjaxModelLoader(
            'city',
            session,
            City,
            search_field='label',
            page_size=10,
            placeholder='Commencer la saisie puis sélectionner une ville...',
            allow_blank=True
        )
    }

    # add checkbox to select the type of address (french by default)
    form_extra_fields = {
        "not_french_address": BooleanField(
            label="Adresse hors France ?",
            render_kw={"id": "not_french_address"}
        )
    }

    def on_model_change(self, form, model, is_created):
        model.last_editor = current_user.username
        session.commit()


class CityView(GlobalModelView):
    list_template = "admin/list.city.html"
    column_list = ["id",
                   "_id_dil",
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
                   "siaf_id",
                   ] + list(version_metadata.keys())

    column_labels = {
        "id": "ID",
        "_id_dil": "ID DIL",
        "label": "Libellé",
        "country_iso_code": "Code ISO du pays",
        "long_lat": "Coordonnées géographiques (longitude, latitude)",
        "insee_fr_code": "Code INSEE",
        "insee_fr_department_code": "Code du département (INSEE)",
        "insee_fr_department_label": "Libellé du département (INSEE)",
        "geoname_id": "Identifiant Geonames",
        "wikidata_item_id": "Identifiant Wikidata",
        "dicotopo_item_id": "Identifiant Dicotopo (ENC)",
        "databnf_ark": "ARK BNF",
        "viaf_id": "Identifiant VIAF",
        "siaf_id": "Identifiant SIAF",
        **version_metadata
    }

    column_searchable_list = ["label"]

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
        ''') if m.long_lat else "(Pas de coordonnées disponibles)"),
        "insee_fr_code": lambda v, c, m, p: _format_href(
            label=m.insee_fr_code,
            prefix_url="https://www.insee.fr/fr/metadonnees/geographie/commune/"
        ),
        "insee_fr_department_code": lambda v, c, m, p: _format_href(
            label=m.insee_fr_department_code.replace("DEP_", ""),
            prefix_url="https://www.insee.fr/fr/metadonnees/geographie/departement/"
        ),
        "geoname_id": lambda v, c, m, p: _format_href(
            label=m.geoname_id,
            prefix_url="https://www.geonames.org/"
        ),
        "wikidata_item_id": lambda v, c, m, p: _format_href(
            label=m.wikidata_item_id,
            prefix_url="https://www.wikidata.org/wiki/"
        ),
        "dicotopo_item_id": lambda v, c, m, p: _format_href(
            label=m.dicotopo_item_id,
            prefix_url="https://dicotopo.cths.fr/places/"
        ),
        "databnf_ark": lambda v, c, m, p: _format_href(
            label=m.databnf_ark,
            prefix_url="https://data.bnf.fr/fr/"
        ),
        "viaf_id": lambda v, c, m, p: _format_href(
            label=m.viaf_id,
            prefix_url="https://viaf.org/fr/viaf/"
        ),
        "siaf_id": lambda v, c, m, p: _format_href(
            label=m.siaf_id,
            prefix_url="https://francearchives.gouv.fr/fr/location/"
        )
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
            "validators": [validate_coordinates],
            "label": "Coordonnées géographiques (longitude, latitude)",
            "description": "Coordonnées géographiques de la ville (longitude, latitude). "
        },
        "insee_fr_code": {
            "validators": [is_only_digits],
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
            "validators": [is_only_digits],
            "label": "Identifiant Geonames",
            "description": "ID Geonames de la ville. "
                           "Exemple : <a href='https://www.geonames.org/2988507/paris.html' target='_blank'><b>2988507</b></a> pour Paris."
        },
        "wikidata_item_id": {
            "validators": [is_wikidata_qid],
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
            "validators": [is_ark_id],
            "label": "ARK BNF",
            "description": "ARK BNF (catalogue général) de la ville. "
                           "Exemple : <a href='https://catalogue.bnf.fr/ark:/12148/cb15272211b' target='_blank'><b>ark:/12148/cb15272211b</b></a> pour Lyon."
        },
        "viaf_id": {
            "validators": [is_only_digits],
            "label": "Identifiant VIAF",
            "description": "ID VIAF de la ville. "
                           "Exemple : <a href='https://viaf.org/fr/viaf/312739984' target='_blank'><b>131453</b></a> pour Rennes."
        },
        "siaf_id": {
            "validators": [is_only_digits],
            "label": "Identifiant SIAF",
            "description": "ID SIAF de la ville. "
                           "Exemple : <a href='https://francearchives.gouv.fr/fr/location/217180640'><b>217180640</b></a> pour Port-Sainte-Marie (Lot-et-Garonne, France)."
        }
    }


    def on_model_change(self, form, model, is_created):
        model.last_editor = current_user.username
        session.commit()

    def get_list(self, page, sort_field, sort_desc, search, filters, page_size=None):
        query = self.session.query(self.model)
        all_rows = query.all()

        if search:
            normalized_search = unidecode(search).lower().strip()
            search_tokens = normalized_search.split()

            def match(row):
                combined = f"{row.label or ''}"
                normalized_combined = unidecode(combined).lower()
                return all(token in normalized_combined for token in search_tokens)

            filtered_rows = list(filter(match, all_rows))
        else:
            filtered_rows = all_rows

        count = len(filtered_rows)

        # Tri optionnel
        if sort_field:
            reverse = sort_desc
            filtered_rows.sort(
                key=lambda x: getattr(x, sort_field, '').lower() if getattr(x, sort_field) else '',
                reverse=reverse
            )

        # Pagination Python
        if page_size:
            start = page * page_size
            end = start + page_size
            filtered_rows = filtered_rows[start:end]

        return count, filtered_rows


class AboutView(BaseView):
    """Custom view for database documentation."""

    @expose('/')
    def index(self):
        """Renders automatic documentation of database in html view."""
        return self.render('admin/about/documentation_db.html')

    @expose('/')
    def database_documentation(self):
        """Renders automatic documentation of database in html view."""
        return self.render('admin/about/documentation_db.html')

    @expose('/contacts')
    def contacts(self):
        """Renders contacts in html view."""
        return self.render('admin/about/contacts.html')

    @expose('/credits')
    def credits(self):
        """Renders credits in html view."""
        return self.render('admin/about/credits.html')
