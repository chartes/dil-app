# dil-app backend service

![Python versions](https://img.shields.io/badge/python-3.10-blue) [![DIL API CI](https://github.com/chartes/dil-app/actions/workflows/CI-tests.yml/badge.svg)](https://github.com/chartes/dil-app/actions/workflows/CI-tests.yml) ![Dil-Coverage](./tests/coverage.svg)

[![FastAPI - API](https://img.shields.io/static/v1?label=FastAPI&message=API&color=%232E303E&style=for-the-badge&logo=fastapi&logoColor=%23009485)](https://fastapi.tiangolo.com/)
[![SQLite - DB](https://img.shields.io/static/v1?label=SQLite&message=DB&color=%2374B8E4&style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![Flask - admin](https://img.shields.io/static/v1?label=Flask&message=admin&color=black&style=for-the-badge&logo=flask&logoColor=white)](https://flask-admin.readthedocs.io/en/latest/#)
[![SQLAlchemy -  orm](https://img.shields.io/badge/SQLAlchemy-_orm-red?style=for-the-badge)](https://www.sqlalchemy.org/)

## Description

Ce dépôt forme le *backend* de l'application dictionnaire des imprimeurs lithographes du XIXe siècle en France, qui se décline de la manière suivante :
- le modèle et la base de données SQLite;
- l'interface d'administration pour la BD;
- l'API (+ documentation Swagger).



## Historique 

Le projet du Dictionnaire des imprimeurs lithographes a été conçu dans le cadre d'une réflexion engagée au sein du Labex CAP sur le rôle des reproductions et illustrations dans histoire de l'art. Pour juger de l'influence des nouveaux procédés d’illustration sur la formation du regard, il a paru utile de mieux connaitre la façon dont l'impression lithographique s'est répandue en France ainsi que l'importance et la nature de sa production. 

La base de données constituée grâce aux crédits du Labex CAP est hébergée et régulièrement enrichie par l'École des chartes - PSL, au fil des dépouillements d'archives. Interrogeable sur plusieurs critères, elle offre aux chercheurs un ensemble de plus de 5 500 notices concernant les imprimeurs lithographes installés en France au XIXe siècle.

### Chronologie

**janvier 2014** : Début du projet et création de l'application (PHP-Drupal+MySQL+Apache) hébergé sur http://elec.enc.sorbonne.fr/imprimeurs/ 

**août 2024** : Début migration de l'application -> traitement des données

**janvier 2025** : Données migrées en base -> création de la plateforme d'administration des données + réflexion sur le frontend
