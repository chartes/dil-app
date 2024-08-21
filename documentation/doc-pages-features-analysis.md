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

- texte de présentation en HTML 
- bandeau de navigation : accès aux pages suivantes
- logos : ENC et Labex CAP (aucun lien fonctionnel)


## [imprimeurs/recherche/](http://elec.enc.sorbonne.fr/imprimeurs/recherche/) : Page de recherche

**page dynamique**

- formulaire de recherche : rechercher des imprimeurs avec champs de recherche : 
  - Nom 
  - Ville-Département
  - Adresses professionnelles
  - Informations personnelles
  - Informations professionnelles
  - Date de début d'activité
  - Date de fin d'activité
  - En activité à une date donnée
+ boutton de recherche et de réinitialisation du formulaire

- recherche par ordre alphabétique (lettres de l'alphabet)

- résultats de recherche : liste des imprimeurs dans un tableau avec les colonnes suivantes :
  - Nom  => fonction de tri 
  - Prénom 
  - Date de début d'activité : ISO fr, null opt 
  - Date de fin d'activité : ISO fr, null opt

- pagination (50 résultats par page)

## [imprimeurs/dictionnaire/](http://elec.enc.sorbonne.fr/imprimeurs/dictionnaire/) : Dictionnaire des imprimeurs

**page dynamique**

- cartes des imprimeurs par ordre alphabétique (50 max.) avec pagination sur la lettre
  - Nom : obligatoire
  - Prénom(s) : obligatoire 
  - Date (début de l'activité) : opt.
  - Ville (parfois avec département entre parenthèses) : obligatoire
  - adresses professionnelles :  opt.
  - adresse personnelle : opt.
  - informations personnelles :  opt. rich text
  - informations professionnelles : opt. rich text
  - image titre / illustration : opt.

## [imprimeurs/node/21538](http://elec.enc.sorbonne.fr/imprimeurs/node/21538) : Fiche d'un imprimeur

**page dynamique**

- image titre : optionnel (mapping : )

- fiche d'un imprimeur
  - Titre : concaténation Nom Prénom(s) 
  - Nom : obligatoire 
  - Prénom(s) : obligatoire
  - Date début activité : opt., ISO fr.
  - Date fin activité : opt., ISO fr. 
  - adresses professionnelles : opt. ex. 
  - Ville - département : obligatoire 
  - Prédécesseur(s) : opt.
  - Successeur(s) : opt.
  - Parrain(s) : opt.
  - informations personnelles : opt. rich text
  - informations professionnelles : opt. rich text
  - Bibliographie Sources : opt.
  - Iconographie : optionnel (mapping : ) liste de références icono sur catalogue.bnf attention ne correspond pas forcemment au caroussel 

- caroussel d'images (optionnel) mapping : ?

## [imprimeurs/node/24767](http://elec.enc.sorbonne.fr/imprimeurs/node/24767) : Page mode d'emploi 

**page statique**

- textes avec niveau de titres html 

## [imprimeurs/node/24769](http://elec.enc.sorbonne.fr/imprimeurs/node/24769) : Page crédits / contact

**page statique**

- textes avec niveau de titres html