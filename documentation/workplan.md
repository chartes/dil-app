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
- [X] Table Address
  - [X] Nettoyer les adresses pro manuellement
  - [X] Nettoyer les adresses perso manuellement
  - [X] Créer la table de référence Address
  - [X] Faire les relations avec les patents et les personnes
- [X] Table relation person_has_addresses
- [X] Table relation patent_has_images
- [X] Table relation patent_has_addresses
- [X] Table relation patent_has_relations
- [X] Filtre et backup des images (dans Drupal) => arrangement table Image
- [X] Backup des données netoyées et préparées

## Modélisation de la base de données avec SQLAlchemy

- [X] Faire tests de manifeste IIIF avec liens IIIF et images dans le système de fichier => selon revoir la modélisation SQL
- [X] Esquisse d'un modèle SQLAlchemy (traduction des tables MySQL en classes SQLAlchemy, relations, contraintes) proposé deux versions (simple et élaboré (images et adresse)) avec les schémas dans [schemas/](Proposal/schemas) et dans `models/`
- [X] Modélisation des relations entre les tables
- [X] Modélisation des contraintes (non-circulaire, unique etc.)
- [X] Migration des données propres dans SQLite -> ajustements modèle

---
- [X] **Validation étape**
---

## Flask-Admin et API

- [X] Mise en place flask-admin
- [ ] Finalisation du formulaire de création imprimeur et villes + refactorisation
- [ ] Finalisation des pages : consulation des imprimeurs, acceuil et documentation et sup des tables inutiles dans le front admin
- [ ] Ajout de la logique user (login)
- [ ] Tests CRUD (fixtures) + ajustements modèle

- [ ] Conception API (routes et db async !!! + schemas) + doc (ajout dans l'admin du lien vers la doc) [doc-routes-api-REST-proposal.md](Proposal/doc-routes-api-REST-proposal.md)
- [ ] Tests API (fixtures) + ajustements modèle
- [ ] Préparer environnement de développement et production
- [ ] Readme
- [ ] Déploiement sur serveur de dev
- 
---
- [ ] **Validation étape**
---

## Mise en œuvre de l'application 

- [ ] Ouvrir projet Vue.js + dépot Git
- [ ] Mise en place de l'application Vue.js (reprendre doc réunion 9/01/2025 avec EP)


## Maintenance, tests, retours utilisateurs

- [ ] corrections, Nouvelles fonctionnalités ?