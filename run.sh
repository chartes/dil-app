#!/bin/bash

###################################################################################
#                                                                                 #
# run.sh                                                                          #
# ----------                                                                      #
#                                                                                 #
# ** API main launch script **                                                    #
#                                                                                 #
# Usage:                                                                          #
#   ./run.sh <mode> [-db]                                                         #
#   <mode> : dev | prod [REQ.]                                                    #
#   -db-re | -db-back : Recreate and populate database with initial               #
#   data (from ressources or from db backup) [OPT.]                               #
#   instance : launch with uvicorn instance on ENC server (dev/prod) [OPT.]       #
#                                                                                 #
# Examples:                                                                       #
#   ./run.sh dev -db                                                              #
###################################################################################

ENV="dev"
DB="./db/DIL.db"
DB_BACKUP="./db/DIL.db"
INSTANCE="/srv/webapp/api/endp-person-app/venv/bin/uvicorn"

# ajouter une commande help afficher l'aide
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  echo "run.sh - API main launch script"
  echo "Usage: ./run.sh <mode> [-db]"
  echo "  <mode> : dev | prod [REQ.]"
  echo "  -db-re | -db-back : Recreate and populate database with initial data (from ressources or from db backup) [OPT.]"
  echo " instance : launch with uvicorn instance on ENC server (dev/prod) [OPT.]"
  exit 0
fi



# Lancer l'application en fonction du mode
echo "Loading vars env in "$1" mode..."
case "$1" in
  dev)
    ENV="dev"
    DB="./db/endp.dev.sqlite"
    source .dev.env
    ;;
  prod)
    ENV="prod"
    DB="./db/endp.prod.sqlite"
    INSTANCE="/srv/webapp/endp-person-app/venv/bin/uvicorn"
    source .prod.env
    ;;
  *)
    echo "Invalid mode. Please specify either 'dev' or 'prod'."
    exit 1
    ;;
esac

export ENV=$ENV

# Vérification de l'argument pour la base de données
if [[ "$2" == "-db-re" ]]; then
  echo "=*= Database recreate and populate from csv ressources =*="
  echo "> Prepare whoosh index dir..."
  python3 manage.py index-create
  echo "> Recreate database process:"
  python3 manage.py db-recreate
  echo "> Populate database process:"
  python3 manage.py db-populate
  # whoosh index auto populate via sqlalchemy events
fi

if [[ "$2" == "-db-back" ]]; then
  echo "=*= Database recreate and populate from db backup =*="
  echo "> Prepare whoosh index dir..."
  python3 manage.py index-create
  echo "> Recreate database process:"
  python3 manage.py db-recreate
  echo "> copy database process from backup:"
  python3 manage.py db_copy $DB_BACKUP $DB
  echo "> populate index with copy:"
  python3 manage.py index-populate
  # whoosh index auto populate via sqlalchemy events
fi


# Lancer l'application en fonction du mode
echo "Starting the application [in "$1" mode]..."
if [[ "$3" == "instance" || "$2" == "instance" ]]; then
  echo "> run with instance..."
  $INSTANCE api.main:app --host $HOST --port $PORT --workers $WORKERS
  #uvicorn api.main:app --host $HOST --port $PORT --workers $WORKERS
else
  if [[ "$ENV" == "dev" ]]; then
    uvicorn api.main:app --host $HOST --port $PORT --reload
  elif [[ "$ENV" == "prod" ]]; then
    uvicorn api.main:app --host $HOST --port $PORT --workers $WORKERS
  fi
fi



