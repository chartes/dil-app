"""
This main module contains the admin interface generation
with flask-admin to manage the database.
"""
from flask import Flask

from flask_admin import Admin
#from flask_babel import Babel
from flask_babelex import Babel
from flask_login import LoginManager
from flask_mail import Mail

#from ..crud import get_user
from api.config import BASE_DIR
from .views import *

# flask app #
flask_app = Flask(__name__,
                  template_folder=BASE_DIR / 'api/templates',
                  static_folder=BASE_DIR / 'api/static')

# flask configuration #
flask_app.config['SECRET_KEY'] = str(settings.FLASK_SECRET_KEY)
flask_app.config['BABEL_DEFAULT_LOCALE'] = str(settings.FLASK_BABEL_DEFAULT_LOCALE)
flask_app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Paris'
flask_app.config['FLASK_ADMIN_BASE_TEMPLATE'] = 'admin/master.html'
#flask_app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
#flask_app.config['MAIL_SERVER'] = str(settings.FLASK_MAIL_SERVER)
#flask_app.config['MAIL_PORT'] = int(settings.FLASK_MAIL_PORT)
#flask_app.config['MAIL_USE_TLS'] = bool(settings.FLASK_MAIL_USE_TLS)
#flask_app.config['MAIL_USE_SSL'] = bool(settings.FLASK_MAIL_USE_SSL)
#flask_app.config['MAIL_USERNAME'] = str(settings.FLASK_MAIL_USERNAME)
#flask_app.config['MAIL_PASSWORD'] = str(settings.FLASK_MAIL_PASSWORD)

# flask extensions #
Babel(flask_app)
admin = Admin(flask_app,
              name="DIL DB Administration",
              template_mode="bootstrap3",
              url="/dil/admin/",
              endpoint="admin",
              index_view=AdminView()
        )
login = LoginManager(flask_app)
mail = Mail(flask_app)


@login.user_loader
def load_user(user_id):
    """load the user with the given id"""
    return get_user(session, {'id': user_id})


# Register views #
for view in [
    PrinterView(Person,
               session,
               name='Imprimeurs',
               menu_icon_type='glyph',
               menu_icon_value='glyphicon-user',
               endpoint='person'),
    #PatentView(Patent,
    #           session,
    #           name='Brevets'),
    CityView(City,
             session,
             name='Villes',
             category='Référentiels',
             endpoint='city',
                menu_icon_type='glyph',
                menu_icon_value='glyphicon-globe'
             ),
    AddressView(Address,
                session,
                name='Adresses',
                category='Référentiels',
                endpoint='address',
                menu_icon_type='glyph',
                menu_icon_value='glyphicon-home'),
    ImageView(Image,
              session,
              name='Gestion des images',
              menu_icon_type='glyph',
              menu_icon_value='glyphicon-picture'),
    UserView(User,
             session,
             name='Utilisateurs',
             menu_icon_type='glyph',
             menu_icon_value='glyphicon-cog'),
    #PatentHasRelationsView(PatentHasRelations,
    #                       session,
    #                       name='Relation entre brevets',
    #                       category='Relations'),
    #ModelView(PersonHasAddresses,
    #          session,
    #          name='Personne-Adresse',
    #          category='Relations'),
    #ModelView(PatentHasAddresses,
    #          session,
    #          name='Brevet-Adresse',
    #          category='Relations'),
    #PatentHasImagesView(PatentHasImages,
    #                    session,
    #                    name='Brevet-Image',
    #                    category='Relations'),
]:
    admin.add_view(view)

#from .routes import reset_password, reset_password_request
