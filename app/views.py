from flask_admin.contrib.sqla import ModelView

class GlobalModelView(ModelView):
    """Global & Shared parameters for the model views."""
    column_display_pk = True
    can_view_details = True
    can_set_page_size = False
    action_disallowed_list = ['delete']
    #list_template = 'admin/list.html'
    can_edit = True
    can_delete = True
    can_create = True
    can_export = True

class PersonView(GlobalModelView):
    """View for the person model."""
    #edit_template = 'admin/edit.html'
    #create_template = 'admin/edit.html'
    #list_template = 'admin/person_list.html'
    #details_template = 'admin/person_details.html'
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
                        "firstnames": "Prénoms",
                        "birth_date": "Date de naissance",
                        "birth_city_label": "Ville de naissance",
                        "birth_city_id": "ID Ville de naissance",
                     "personal_information": "Informations personnelles",
                        "professional_information": "Informations professionnelles",
                        "comment": "Commentaire",
                        "created_at": "Créé le",
                        "updated_at": "Modifié le",
                        "last_editor": "Dernier éditeur"
                     }
