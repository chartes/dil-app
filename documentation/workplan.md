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

## Flask-Admin

- [X] Mise en place flask-admin


- [X] Finaliser formulaire Imprimeur (CRUD)
    - pour l'ajout d'image bug quand on enlève la dernière image le thumbnail reste dans le carrousel + le pinned marche après deux enregistrement
    - validateurs
    - champs
    - relations
    - renvoi vers autre formulaire au besoin
- [X] Finaliser formulaire Ville (CRUD) WIP
  - validateurs à ajouter
  - champs
- [X] Finaliser formulaire Adresses (CRUD)
  - validateurs
  - champs (ajouter le Select2)
- [X] Finaliser formulaire Image (CRUD)
  - attention quand on supprime l'image elle reste dans le dir
  - check les relations ondelete
  - validateurs
  - champs
- [X] Ajouter logique de connexion (table User, login, logout, roles)
- [X] revoir les tests
- [X] régler le not found http://127.0.0.1:8888/admin/ --> http://127.0.0.1:8888/dil/admin/ (icone menu)
- [X] remettre les tests
- [ ] Finir page consultation personne
- [ ] Finaliser en savoir plus (documentation db, juste le schéma)
- [ ] Commencer API se baser sur site actuel + reprendre besoin pour ajusteent plus tard
- [ ] Refactoriser et nettoyage (local et distant) (admin, modèles, vues, scripts, template)
- [ ] Préparer fichiers de config dev et prod
- test de la base async pour le crud et alembic qui fonctionne pas
- [ ] Déploiement sur serveur de dev + fichiers de config dev et prod + scripts de création de la base ou migration de la base a vérifier
- [ ] optimisation
---
- [ ] **Validation étape VJ et reprise + test utilisateur (EP)**
---
- [ ] Correction + données manquantes (Cf. issues)

## Mise en œuvre de l'application

- [ ] API à mettre en place et index si besoin
- [ ] Ouvrir projet Vue.js / Vite + dépot Git
- [ ] Mise en place de l'application Vue.js (reprendre doc réunion 9/01/2025 avec EP)

## Maintenance, tests, retours utilisateurs

- [ ] corrections, Nouvelles fonctionnalités ?