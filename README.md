# dil-app backend service

![Python versions](https://img.shields.io/badge/python-3.9-blue) [![DIL API CI](https://github.com/chartes/dil-app/actions/workflows/CI-tests.yml/badge.svg)](https://github.com/chartes/dil-app/actions/workflows/CI-tests.yml) ![Dil-Coverage](./tests/coverage.svg)

[![FastAPI - API](https://img.shields.io/static/v1?label=FastAPI&message=API&color=%232E303E&style=for-the-badge&logo=fastapi&logoColor=%23009485)](https://fastapi.tiangolo.com/)
[![SQLite - DB](https://img.shields.io/static/v1?label=SQLite&message=DB&color=%2374B8E4&style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![Flask - admin](https://img.shields.io/static/v1?label=Flask&message=admin&color=black&style=for-the-badge&logo=flask&logoColor=white)](https://flask-admin.readthedocs.io/en/latest/#)
[![SQLAlchemy -  orm](https://img.shields.io/badge/SQLAlchemy-_orm-red?style=for-the-badge)](https://www.sqlalchemy.org/)

## Description

Ce dépôt forme le *backend* de l'application dictionnaire des imprimeurs lithographes du XIXe siècle en France, qui se décline de la manière suivante :
- le modèle et la base de données SQLite;
- l'interface d'administration pour la BD;
- l'API (+ documentation Swagger).


## Installation

En local, cloner le dépôt GitHub :

```bash
git clone git@github.com:chartes/dil-app.git
```

Puis exécuter les commandes suivantes :

```bash
virualenv --python=python3.9 venv
source venv/bin/activate
pip install -r requirements.txt
 ```

## Lancer l'API

Les tâches courantes sont réalisées avec le script `run.sh`.

Pour une première initialisation de la base de données ou pour la recréer et lancer l'application :

```bash
   ./run.sh dev -db-re -images-back
```

- `-db-re` : recréer la base de données avec les données initiales (attention si la base de données existe déjà, elle sera écrasée ou si des données ont été ajoutées ou modifiées, elles seront perdues);
- `-images-back` : copier les images intiales de la base de données dans le dossier `static` pour les rendre accessibles via l'API.
- `-create-index` : créer les index de la base de données (nécessaire pour les recherches sur les champs texte).

Pour lancer l'application seule (ignorer l'argument `-db-re`, `-create-index` et `-images-back`) :

```bash
   ./run.sh dev
```

Pour contrôler le bon fonctionnement de l'application :

- la documentation de l'API se trouve à l'adresse : http://127.0.0.1:9090/dil/api/docs
- l'interface d'administration se trouve à l'adresse : http://127.0.0.1:9090/dil/admin/

Identifiants par défaut pour l'authentification à l'interface d'administration 
pour le développement et les tests :

- username : `admin`
- password : `admin`

> [!WARNING]  
> Les identifiants par défaut ne sont pas sécurisés, il est recommandé de les modifier en dev ou en prod.

## Gestion des utilisateurs

- Ajouter ou supprimer un utilisateur 
- Modifier un mot de passe

Ces actions sont disponibles dans l'interface d'administration de l'application, si la connexion s'effectue
avec un compte ayant les droits d'administration.


## Contrôle de la qualité du code et tests unitaires

La qualité du code et les tests unitaires sont réalisés via la CI GitHub Actions.
Cependant, pour lancer les tests en local : 

```bash
cd tests/
# 1. lancer le contrôle de la qualité du code
# rendre le scripts exécutable (si nécessaire)
chmod +x tests.sh
./tests.sh
# pour générer le badge de couverture de code
coverage-badge -o coverage.svg
```

## Historique 

Le projet du Dictionnaire des imprimeurs lithographes a été conçu dans le cadre d'une réflexion engagée au sein du Labex CAP sur le rôle des reproductions et illustrations dans histoire de l'art. Pour juger de l'influence des nouveaux procédés d’illustration sur la formation du regard, il a paru utile de mieux connaitre la façon dont l'impression lithographique s'est répandue en France ainsi que l'importance et la nature de sa production. 

La base de données constituée grâce aux crédits du Labex CAP est hébergée et régulièrement enrichie par l'École des chartes - PSL, au fil des dépouillements d'archives. Interrogeable sur plusieurs critères, elle offre aux chercheurs un ensemble de plus de 5 500 notices concernant les imprimeurs lithographes installés en France au XIXe siècle.

### Chronologie

**janvier 2014** : Début du projet et création de l'application (PHP-Drupal+MySQL+Apache) hébergé sur http://elec.enc.sorbonne.fr/imprimeurs/ 

**août 2024** : Début migration de l'application -> traitement des données

**janvier 2025 -** : Données migrées en base -> création de la plateforme d'administration des données + réflexion sur le frontend
