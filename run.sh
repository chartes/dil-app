#!/bin/bash

###################################################################################
# run.sh - API main launch script                                                 #
###################################################################################

# Configuration des chemins et variables par défaut
ENV="dev"
DB="./db/dil.dev.sqlite"
DB_BACKUP="./db/DIL.db"
INSTANCE="/srv/webapp/api/endp-person-app/venv/bin/uvicorn"
IMAGE_ORIGINAL_DIR="./data/assets/images/"
IMAGE_API_DIR="./api/static/images_store/"

# Afficher l'aide
usage() {
  echo "Usage: ./run.sh <mode> [-db-re] [-db-back] [-images-back] [instance]"
  echo "  <mode>       : dev | prod (Obligatoire)"
  echo "  -db-re       : Recreate and populate database from resources"
  echo "  -db-back     : Restore database from backup"
  echo "  -images-back : Restore original images from backup"
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

# Gérer les options supplémentaires
for arg in "$@"; do
  case "$arg" in
    -db-re)
      echo "Recreating and populating database..."
      [[ -f $DB ]] && rm $DB
      python3 -m scripts.create_db --db $DB
      echo "Database setup complete."
      ;;
    -db-back)
      echo "Restoring database from backup..."
      cp "$DB_BACKUP" "$DB"
      echo "Database restored."
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
