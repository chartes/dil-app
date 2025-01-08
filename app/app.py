from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from models_archive.models import *
from pathlib import Path

from views import *

# Initialisation de l'application Flask
BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
app = Flask(__name__,
            template_folder=BASE_DIR / 'templates',
            static_folder=BASE_DIR / 'static'
            )
app.config['SECRET_KEY'] = 'secret'  # Clé secrète pour Flask-Admin
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'

# Configuration de la base de données SQLite
DATABASE_URL = "sqlite:///./models_archive/db/DIL.db"
engine = create_engine(DATABASE_URL)
Session = scoped_session(sessionmaker(bind=engine))

# Créer la session Flask-Admin
Babel(app)
admin = Admin(app,
              name='DIL DB Administration',
              template_mode='bootstrap3')

# Ajouter vos modèles à l'interface Flask-Admin
admin.add_view(PersonView(Person, Session, name='Imprimeurs',menu_icon_type='glyph',
               menu_icon_value='glyphicon-user'))
admin.add_view(ModelView(Patent, Session, name='Brevets'))
admin.add_view(ModelView(City, Session, name='Villes'))
admin.add_view(ModelView(Address, Session, name='Adresses'))
admin.add_view(ModelView(Image, Session, name='Images'))

# Lancer le serveur Flask
if __name__ == '__main__':
    app.run(debug=True)
