# DIL-ELEC-analysis : Analyse et mapping de la base MySQL en vue de la migration vers SQLITE

- Le mapping des tables principales de la base MySQL est disponible dans le fichier [doc-mapping-database-analysis.ods](doc-mapping-database-analysis.ods)

Les 20 tables principales à récupérer sont les suivantes :

- main `node` : id imprimeur + nom de l'imprimeur 
- main `field_data_field_nom` : nom de l'imprimeur (voir aussi `node`) 
- main `field_data_field_pr_nom` : prénom de l'imprimeur
- main `field_data_field_date_de_d_but_du_brevet` : date de début d'activité de l'imprimeur
- main `field_data_field_date_de_fin_du_brevet` : date de fin d'activité de l'imprimeur
- main `field_data_field_ville` : ville d'exercice de l'imprimeur
- main > table_specific ? `field_data_field_adresses_professionnelles` : adresses professionnelles de l'imprimeur
- main > table_specific ? `field_data_field_adresse_personnelle` : adresse personnelle de l'imprimeur
- main `field_data_field_informations_personnelles` : informations personnelles de l'imprimeur
- main `field_data_field_informations_professionnel` : informations professionnelles de l'imprimeur
- TODO specific `field_data_field_illustration` : image-titre ou illustration pour l'imprimeur
- relation `field_data_field_pr_d_ecesseurs` : prédécesseurs de l'imprimeur
- relation `field_data_field_successeurs` : successeurs de l'imprimeur
- relation `field_data_field_parrains` : parrains de l'imprimeur
- relation `field_data_field_associ_s` : associés de l'imprimeur
- main `field_data_field_bibliographie_sources` : bibliographie et sources pour attester de l'imprimeur
- main `field_data_field_remarques` : notes libres de l'utilisateur sur l'imprimeur
- relation `field_data_field_autres_brevets` : autres brevets de l'imprimeur (liens vers les imprimeurs)
- TODO specific `field_data_field_iconographie_2` : iconographie de l'imprimeur présente sous forme de liens HREF dans la notice
- TODO specific `field_data_field_illustration2` : images disponibles dans le carroussel 
- TODO specific `file_managed` : images disponibles en local (path URI, filename, fid) utiles comme pivot pour les tables : 
  - `field_data_field_illustration` : image-titre ou illustration pour l'imprimeur
  - `field_data_field_illustration2` : images disponibles dans le carroussel
  - `field_data_field_iconographie_2` : iconographie de l'imprimeur présente sous forme de liens HREF dans la notice


- Pour les tables restantes : 

- other `field_data_body` : données des champs de texte des pages
- OK `field_data_field_arrdt` : arrondissements (pas utilisés) voir `node/22978` par exemple
- OK `field_data_field_date_de_naissance` : dates de naissance de l'imprimeur en ISO (pas utilisées) voir `node/22032` par exemple
- OK `field_data_field_lieu_de_naissance` : lieux de naissance de l'imprimeur (pas utilisés) voir `node/26141` par exemple
- OK `field_data_field_parcours_professionnel` : parcours professionnel de l'imprimeur (pas utilisé) sous la forme d'un texte formaté en HTML, énumération de métiers voir `node/22505` par exemple