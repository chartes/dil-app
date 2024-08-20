# Workplan

## Planification et mise en place du dépôt

- [X] refaire fonctionner elec (donner un `sudo service apache2 restart`)
- [X] Dépôt GitHub initialisé
- [ ] Documentation de la structure actuelle de la base de données (mapping des champs) dans [doc-mapping-database-analysis.csv](doc-mapping-database-analysis.csv)
- [X] Analyse des fonctionnalités actuelles de l'application à répercuter dans [doc-pages-features-analysis.md](doc-pages-features-analysis.md)
- [X] Mise en place arborescence de l'application
      
## Modélisation de la base de données avec SQLAlchemy

- [ ] Esquisse du modèle SQLAlchemy (traduction des tables MySQL en classes SQLAlchemy, relations, contraintes) proposé deux versions (simple et élaboré) avec les schémas dans [schemas/](schemas) et dans `models/`

## Récupération des données

- [ ] Récupération des données dans les tables de la base MySQL (CSV)
- [ ] Analyse et préparation des données dans Dataiku
- [ ] Backup des données préparées

## Conception schéma applicatif

- [ ] Modélisation de l'architecture de l'application (base de données, administration, routes Flask, templates HTML, API REST, technologies utilisées, relations entre les composants, framework CSS ou VUEJs etc.) inclure (schémas) dans [doc-architecture-proposal.md](doc-architecture-proposal.md)
- [ ] Modélisation de certaines pages HTML inclure liens schémas dans [doc-architecture-proposal.md](doc-architecture-proposal.md)

## Réflexions sur les images et les liens externes

- [ ] Analyse des images associées aux enregistrements (nombre, nommage, formats, status)
- [ ] Analyse des liens externes (Gallica, etc.)
      
##  modélisation API REST

- [ ] Pré-documentation des endpoints de l'API REST dans [doc-routes-api-REST-proposal.md](doc-routes-api-REST-proposal.md)

## Tests de migration de données, gestion admin

- [ ] Mise en place flask-admin
- [ ] migration de données de MySQL à SQLite
- [ ] évaluation CRUD sur les données migrées

## Revue des choix technologiques et des fonctionnalités

- [ ] Revue des choix technologiques
- [ ] Revue des fonctionnalités actuelles
- [ ] Revue du plan d'action

## Mise en œuvre de l'application 

- [ ] Préparer environnement de développement et production
- [ ] Application Flask initiale avec intégration SQLAlchemy 
- [ ] Mise en place des routes principales (accueil, recherche, détail, administration)
- [ ] Intégration des templates HTML
- [ ] Intégration de l'API REST
- [ ] Tests unitaires et fonctionnels
- [ ] Documentation technique et utilisateur

## Maintenance, tests, retours utilisateurs

- [ ] nouvelles fonctionnalités ?

## Stand-by

- Comment migrer les données de MySQL à SQLite ?

> 1) export des données en CSV via `SELECT * FROM table_name INTO OUTFILE '/path/to/file.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';` 2) analyse puis préparation dans Dataiku 3) import dans SQLite


- Comment gérer les images associées aux enregistrements ?
