#!/bin/bash

###################################################################################
# run.sh - API main launch script                                                 #
###################################################################################

# Configuration des chemins et variables par défaut
ENV="dev"
DB="./db/dil.dev.sqlite"
INSTANCE="/srv/webapp/api/dil-app/venv/bin/uvicorn"
IMAGE_ORIGINAL_DIR="./data/assets/images/"
IMAGE_API_DIR="./api/static/images_store/"

# Valeur par défaut si non définie
: "${WORKERS:=1}"

# Afficher l'aide
usage() {
  echo "Usage: ./run.sh <mode> [-db-re] [-db-back] [-images-back] [instance]"
  echo "  <mode>       : dev | prod (Obligatoire)"
  echo "  -db-re       : Recreate and populate database from resources"
  echo "  -create-index : Create the index for the database"
  echo "  -images-back : Restore original images from backup"
  #TODO: add command for index creation and populate
  echo "  instance     : Launch using the ENC server instance"
  exit 0
}

# Vérifier les arguments
if [[ "$1" == "-h" || "$1" == "--help" || -z "$1" ]]; then
  usage
fi

# Définir les variables en fonction du mode
case "$1" in
  dev)
    ENV="dev"
    DB="./db/dil.dev.sqlite"
    source .dev.env
    ;;
  prod)
    ENV="prod"
    DB="./db/dil.prod.sqlite"
    INSTANCE="/srv/webapp/dil-app/venv/bin/uvicorn"
    source .prod.env
    ;;
  *)
    echo "Invalid mode: $1. Use 'dev' or 'prod'."
    exit 1
    ;;
esac

export ENV=$ENV

source ./venv/bin/activate
# Gérer les options supplémentaires
for arg in "$@"; do
  case "$arg" in
    -db-re)
      echo "Recreating and populating database..."
      [[ -f $DB ]] && rm $DB
      python3 -m scripts.create_db --db $DB
      echo "Database setup complete."
      ;;
    -create-index)
      echo "Creating database index..."
      [[ -f $DB ]] || { echo "Database not found. Please create it first."; exit 1; }
      python3 -m scripts.create_index
      echo "Index creation complete."
      ;;
    -images-back)
      echo "Restoring original images directory..."
      # clean all files in the images directory API
      rm -rf $IMAGE_API_DIR*
      # copy all files from the original images directory to the API images directory
      cp -r $IMAGE_ORIGINAL_DIR* $IMAGE_API_DIR
      echo "Images restored."
      ;;
  esac
done

# Lancer l'application
echo "Starting the application in '$ENV' mode..."
# shellcheck disable=SC2199
if [[ " $@ " =~ " instance " ]]; then
  echo "Running with instance..."
  $INSTANCE api.main:app --host $HOST --port $PORT --workers $WORKERS
else
  uvicorn api.main:app --host $HOST --port $PORT --reload
fi
