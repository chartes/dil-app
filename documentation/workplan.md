# Workplan DIL-app

## Planification et mise en place du dépôt

- [X] Refaire fonctionner elec (donner un `sudo service apache2 restart`)
- [X] Dépôt GitHub initialisé
- [X] Documentation de la structure actuelle de la base de données (mapping des tables et colonnes) dans [doc-mapping-database-analysis.md](Analysis/doc-mapping-database-analysis.md) et [doc-mapping-database-analysis.ods](Analysis/doc-mapping-database-analysis.ods)
- [X] Analyse des fonctionnalités actuelles de l'application à répercuter dans [doc-pages-features-analysis.md](Analysis/doc-pages-features-analysis.md)
- [X] Mise en place d'une esquisse d'arborescence de l'application
      
## Modélisation de la base de données avec SQLAlchemy

- [X] Esquisse d'un modèle SQLAlchemy (traduction des tables MySQL en classes SQLAlchemy, relations, contraintes) proposé deux versions (simple et élaboré (images et adresse)) avec les schémas dans [schemas/](Proposal/schemas) et dans `models/`

=> Validation ici ?

## Récupération des données

- [X] Récupération des tables de la base MySQL (export CSV) dans [data/](../../data)
- [ ] Import, analyse et préparation des données dans Dataiku
- [ ] Analyse des images associées aux enregistrements (nombre, nommage, formats, status)
- [ ] Analyse des liens externes et enrichissements si possible (Gallica, etc.)
- [ ] Backup des données netoyées et préparées

## Tests de migration de données, gestion admin

- [ ] Mise en place flask-admin
- [ ] Migration de données de MySQL à SQLite
- [ ] Évaluation CRUD sur les données migrées

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