#!/bin/bash

# Usage : ./import_tables.sh chemin_vers_la_base.sqlite chemin_du_dossier_des_fichiers chemin_du_log

DB_PATH=$1
DATA_DIR=$2
LOG_FILE=$3

# Vérifier que les arguments nécessaires sont fournis
if [[ $# -lt 3 ]]; then
  echo "Usage : ./import_tables.sh chemin_vers_la_base.sqlite chemin_du_dossier_des_fichiers chemin_du_log"
  exit 1
fi

# Initialiser le fichier de log
echo "==== Début de l'importation : $(date) ====" >> "$LOG_FILE"

# Vérifier que la base de données et le dossier existent
if [[ ! -f "$DB_PATH" ]]; then
  echo "$(date) - ERREUR : La base de données $DB_PATH n'existe pas." | tee -a "$LOG_FILE"
  exit 1
fi

if [[ ! -d "$DATA_DIR" ]]; then
  echo "$(date) - ERREUR : Le dossier contenant les fichiers $DATA_DIR n'existe pas." | tee -a "$LOG_FILE"
  exit 1
fi

# Liste des tables et des fichiers associés (nom_table=fichier.csv ou fichier.tsv)
declare -A TABLES
TABLES=(
  ["table1"]="table1.csv"
  ["table2"]="table2.tsv"
  ["table3"]="table3.csv"
)

# Import des fichiers dans les tables
for TABLE in "${!TABLES[@]}"; do
  FILE=${TABLES[$TABLE]}
  FILE_PATH="$DATA_DIR/$FILE"

  if [[ ! -f "$FILE_PATH" ]]; then
    echo "$(date) - ERREUR : Le fichier $FILE_PATH n'existe pas. Table $TABLE ignorée." | tee -a "$LOG_FILE"
    continue
  fi

  echo "$(date) - Importation du fichier $FILE_PATH dans la table $TABLE..." | tee -a "$LOG_FILE"

  # Déterminer le séparateur (tab ou virgule)
  if [[ $FILE == *.tsv ]]; then
    SEPARATOR="\t"
  else
    SEPARATOR=","
  fi

  # Compter les lignes dans le fichier TSV
  LINES_IN_FILE=$(wc -l < "$FILE_PATH")

  # Commande sqlite3 pour importer le fichier
  sqlite3 "$DB_PATH" <<EOF
.mode csv
.separator "$SEPARATOR"
.import $FILE_PATH $TABLE
EOF

  # Vérification des lignes insérées
  LINES_IN_TABLE=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM $TABLE;")

  if [[ "$LINES_IN_FILE" -eq "$LINES_IN_TABLE" ]]; then
    echo "$(date) - SUCCÈS : Table $TABLE importée. Lignes dans le fichier : $LINES_IN_FILE, Lignes dans la table : $LINES_IN_TABLE" | tee -a "$LOG_FILE"
  else
    echo "$(date) - ERREUR : Mismatch des lignes pour $TABLE. Fichier : $LINES_IN_FILE, Table : $LINES_IN_TABLE" | tee -a "$LOG_FILE"
  fi
done

echo "==== Fin de l'importation : $(date) ====" >> "$LOG_FILE"
