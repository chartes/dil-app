# Workplan

## Planification et mise en place du dépôt

- [ ] refaire fonctionner elec
- [X] Dépôt GitHub initialisé.
- [ ] Documentation de la structure actuelle de la base de données (mapping des champs)
- [ ] Analyse des fonctionnalités actuelles de l'application à répercuter
- [X] Mise en place arborescence de l'application
- [ ] Esquisse du modèle SQLAlchemy


## Modélisation de la base de données avec SQLAlchemy

- [ ] Création du modèle SQLAlchemy (traduction des tables MySQL en classes SQLAlchemy, relations, contraintes)

## Réflexions sur les images et les liens externes

- [ ] Analyse des images associées aux enregistrements (nombre, nommage, formats, status)
- [ ] Analyse des liens externes (Gallica, etc.)

## Conception du schéma applicatif et modélisation API REST

- [ ] Modélisation de l'architecture de l'application (base de données, administration, routes Flask, templates HTML, API REST, technologies utilisées, relations entre les composants, framework CSS etc.)
- [ ] Pré-documentation des endpoints de l'API REST

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
- Comment gérer les images associées aux enregistrements ?