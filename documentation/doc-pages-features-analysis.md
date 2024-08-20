# Pages

## Sommaire

- [imprimeurs/](#imprimeurs/) : Page d'accueil / présentation (statique)
- [imprimeurs/recherche/](#imprimeurs/recherche/) : Page de recherche (dynamique)
- [imprimeurs/dictionnaire/](#imprimeurs/dictionnaire/) : Page de dictionnaire des imprimeurs (dynamique)
- [imprimeurs/node/21538](#imprimeurs/node/21538) : Page de fiche d'un imprimeur - exemple (dynamique)
- [imprimeurs/node/24767](#imprimeurs/node/24767) : Page mode d'emploi (statique)
- [imprimeurs/node/24769](#imprimeurs/node/24769) : Page crédits / contact (statique)

## [imprimeurs/](http://elec.enc.sorbonne.fr/imprimeurs/) : Page d'accueil / de présentation

**page statique** 

- texte de présentation (provenance ?)
- bandeau de navigation (5 items)
- logos : ENC et Labex CAP (aucun lien)


## [imprimeurs/recherche/](http://elec.enc.sorbonne.fr/imprimeurs/recherche/) : Page de recherche

**page dynamique**

- formulaire de recherche : rechercher des imprimeurs avec champs de recherche : 
  - Nom (mapping : )
  - Ville-Département (mapping : )
  - Adresses professionnelles (mapping : )
  - Informations personnelles (mapping : )
  - Informations professionnelles (mapping : )
  - Date de début d'activité (mapping : )
  - Date de fin d'activité (mapping : )
  - En activité à une date donnée (mapping : )
+ boutton de recherche et de réinitialisation du formulaire

- recherche par ordre alphabétique (lettres de l'alphabet)

- résultats de recherche : liste des imprimeurs dans un tableau avec les colonnes suivantes :
  - Nom (mapping : ) => fonction de tri 
  - Prénom(s) (mapping : )
  - Date de début d'activité : ISO fr, null opt (mapping : )
  - Date de fin d'activité : ISO fr, null opt  (mapping : )

- pagination (50 résultats par page)

## [imprimeurs/dictionnaire/](http://elec.enc.sorbonne.fr/imprimeurs/dictionnaire/) : Dictionnaire des imprimeurs

**page dynamique**

- cartes des imprimeurs par ordre alphabétique (50 max.) avec pagination sur la lettre
  - Nom : obligatoire (mapping : )
  - Prénom(s) : obligatoire (mapping : )
  - Date (début ou fin ?) : obligatoire (mapping : )
  - Ville (département ?) : obligatoire (mapping : )
  - adresses professionnelles : optionnel (mapping : ) ex. 1 adresse (1843 ?)
  - informations personnelles : optionnel (mapping : )  rich text
  - informations professionnelles : optionnel (mapping : ) rich text
  - image : optionnel (mapping : )

## [imprimeurs/node/21538](http://elec.enc.sorbonne.fr/imprimeurs/node/21538) : Fiche d'un imprimeur

**page dynamique**

- image titre : optionnel (mapping : )

- fiche d'un imprimeur
  - Titre : Nom Prénom(s) 
  - Nom : obligatoire (mapping : )
  - Prénom(s) : obligatoire (mapping : )
  - Date début activité : obligatoire, ISO fr. (mapping : )
  - Date fin activité : obligatoire, ISO fr. (mapping : )
  - adresses professionnelles : optionnel (mapping : ) ex. 1 adresse (1843 ?)
  - Ville - département : obligatoire (mapping : )
  - Prédécesseur(s) : optionnel (mapping : )
  - Successeur(s) : optionnel (mapping : )
  - Parrain(s) : optionnel (mapping : )
  - informations personnelles : optionnel (mapping : ) rich text
  - informations professionnelles : optionnel (mapping : ) rich text
  - Bibliographie Sources : optionnel (mapping : )
  - Iconographie : optionnel (mapping : ) liste de références icono sur catalogue.bnf attention ne correspond pas forcemment au caroussel 

- caroussel d'images (optionnel) mapping : ?

## [imprimeurs/node/24767](http://elec.enc.sorbonne.fr/imprimeurs/node/24767) : Page mode d'emploi 

**page statique**

- textes avec niveau de titres html 

## [imprimeurs/node/24769](http://elec.enc.sorbonne.fr/imprimeurs/node/24769) : Page crédits / contact

**page statique**

- textes avec niveau de titres html