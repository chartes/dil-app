# Workplan DIL-app

## Planification et mise en place du dépôt

- [X] Refaire fonctionner elec (donner un `sudo service apache2 restart`)
- [X] Dépôt GitHub initialisé
- [X] Documentation de la structure actuelle de la base de données (mapping des tables et colonnes) dans [doc-mapping-database-analysis.md](Analysis/doc-mapping-database-analysis.md) et [doc-mapping-database-analysis.ods](Analysis/doc-mapping-database-analysis.ods)
- [X] Analyse des fonctionnalités actuelles de l'application à répercuter dans [doc-pages-features-analysis.md](Analysis/doc-pages-features-analysis.md)
- [X] Mise en place d'une esquisse d'arborescence de l'application

## Récupération des données

- [X] Récupération des tables de la base MySQL (export CSV) dans [data/drupal_archive](../../data/drupal_archive)
- [X] Import, analyse et préparation des données dans Dataiku
- [X] Table Person
  - [X] Reste les liens href à nettoyer
- [X] Table Patent
  - [X] Reste les liens href à nettoyer
- [X] Table City
- [X] Table Image
  - [X] Liens IIIF 
  - [X] Merger carrousel avec iconographie
  - [X] Nettoyer la sortie "images_stacked" (entity_id)
  - [X] Filtre des patents inexistants dans la sortie
  - [X] Créer la table de référence des Images
- [ ] Table Address
  - [ ] Nettoyer les adresses pro manuellement
  - [ ] Nettoyer les adresses perso manuellement
  - [ ] Créer la table de référence Address
  - [ ] Faire les relations avec les patents et les personnes
- [ ] Table relation person_has_addresses
- [X] Table relation patent_has_images
- [ ] Table relation patent_has_addresses
- [X] Table relation patent_has_relations
- [ ] Filtre et backup des images (dans Drupal) => arrangement table Image
- [ ] Backup des données netoyées et préparées

## Modélisation de la base de données avec SQLAlchemy

- [X] Faire tests de manifeste IIIF avec liens IIIF et images dans le système de fichier => selon revoir la modélisation SQL
- [X] Esquisse d'un modèle SQLAlchemy (traduction des tables MySQL en classes SQLAlchemy, relations, contraintes) proposé deux versions (simple et élaboré (images et adresse)) avec les schémas dans [schemas/](Proposal/schemas) et dans `models/`
- [X] Modélisation des relations entre les tables
- [ ] Modélisation des contraintes (non-circulaire, unique etc.)
- [ ] Modélisation de la table User
- [ ] ajout de l'abstraction pour les contraintes spécifiques (image)
- [ ] Relecture totale de la modélisation

---
- [ ] **Validation étape**
---

## Tests de migration de données, gestion admin

- [ ] Mise en place flask-admin
- [ ] Migration des données propres dans SQLite -> ajustements modèle
- [ ] Évaluation CRUD sur les données migrées -> ajustements modèle
- [ ] Rédaction de tests

## Conception schéma applicatif

- [ ] Modélisation de l'architecture de l'application (base de données, administration, routes Flask, templates HTML, API REST, technologies utilisées, relations entre les composants, framework CSS ou VUEJs etc.) inclure (schémas) dans [doc-architecture-proposal.md](Proposal/doc-architecture-proposal.md)
- [ ] Modélisation de certaines pages HTML inclure liens schémas dans [doc-architecture-proposal.md](Proposal/doc-architecture-proposal.md)

      
##  modélisation API REST

- [ ] Pré-documentation des endpoints de l'API REST dans [doc-routes-api-REST-proposal.md](Proposal/doc-routes-api-REST-proposal.md)

=> Validation ici ?

## Mise en œuvre de l'application 

- [ ] Préparer environnement de développement et production
- [ ] Application Flask initiale avec intégration SQLAlchemy
- [ ] Intégration de l'API REST
- [ ] Mise en place des routes principales (accueil, recherche, détail, administration)
- [ ] Intégration des templates HTML
- [ ] Tests unitaires et fonctionnels
- [ ] Documentation technique et utilisateur

## Maintenance, tests, retours utilisateurs

- [ ] Nouvelles fonctionnalités ?