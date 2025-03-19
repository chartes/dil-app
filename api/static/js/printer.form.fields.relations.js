/*
*  Patents relations logic
*  -------------------------
*
*  This part implements the logic to add a new relation,
*  delete a relation, load and expose existing relations from
*  admin backend.
*  eg. Acker printer "Successeur" of patent 1 of actuel printer etc.
*  with form fields (Select2 list, btn add and delete etc.)
*
* N.B:
* use : Select2 v3.5.3 (doc link : https://select2.github.io/select2/index.html)
*/


// Gestionnaire de clic sur le bouton principal
$('#patents-button').on('click', function () {
    // Sélectionner tous les conteneurs potentiels
    const containers = document.querySelectorAll("[id^='patents-'][id$='-relation-container']");
    containers.forEach(container => {
        const containerId = container.id;
        let index = containerId.split('-')[1]
        // Vérifie si un bouton d'ajout existe déjà pour ce conteneur
        if (!document.querySelector(`#${containerId} ~ .add-relation-button`)) {
            // Créer et ajouter un bouton d'ajout
            const addButton = createButton("+", ["btn", "btn-primary", "mb-2"], null);
            addButton.classList.add("add-relation-button");
            container.parentElement.appendChild(addButton);

            // Événement pour ajouter une nouvelle relation
            addButton.addEventListener("click", () => addRelationRow(container, addButton, index));
        }
    });
});

// Fonction pour créer un bouton
function createButton(text, classes = [], id = null) {
    const button = document.createElement("button");
    button.textContent = text;
    button.type = "button";
    if (id) button.id = id;
    classes.forEach(cls => button.classList.add(cls));
    return button;
}

// Fonction pour créer un élément <select>
function createSelect(name, options, defaultValue, additionalClasses = []) {
    const select = document.createElement("select");
    select.name = name;
    select.classList.add("form-control", "mr-2", ...additionalClasses);


    options.forEach(optionData => {
        const option = document.createElement("option");
        option.value = optionData.value || optionData.id;
        option.textContent = optionData.label || optionData.name;
        if (defaultValue && option.value === defaultValue.value) {
            option.selected = true;
        }

        select.appendChild(option);
    });

    return select;
}

// Fonction pour ajouter une ligne de relation
function addRelationRow(container, addButton, index) {
    const row = document.createElement("div");
    row.classList.add("relation-row", "mb-3", "d-flex", "align-items-center");

    // Création du champ Select2 AJAX
    const printerSelect = document.createElement("input");
    printerSelect.name = `dynamic_printers[${index}][]`;
    printerSelect.classList.add("form-control", "mr-2", "dynamic-printers");

    // Forcer un champ propre
    printerSelect.innerHTML = ""; // S'assurer que le champ est vide

    // Champ pour types de relation (statique)
    const typeOptions = [
        {value: "PARTNER", label: "Associé"},
        {value: "SPONSOR", label: "Parrain"},
        {value: "SUCCESSOR", label: "Successeur"},
        {value: "PREDECESSOR", label: "Prédécesseur"},
    ];
    const typeSelect = createSelect(`dynamic_relation_types[${index}][]`, typeOptions);

    // Bouton de suppression
    const removeButton = createButton("x", ["btn", "btn-danger", "ml-2"]);
    removeButton.addEventListener("click", () => row.remove());

    // Ajout des éléments à la ligne
    row.appendChild(printerSelect); // Select dynamique
    row.appendChild(typeSelect);   // Select statique
    row.appendChild(removeButton);

    // Insertion de la ligne avant le bouton d'ajout
    container.parentNode.insertBefore(row, addButton);

    // Initialiser Select2 AJAX pour le champ dynamique
    $(printerSelect).select2({
        ajax: {
            url: '/dil/dil/admin/person/get_printers', // URL de la route exposée
            dataType: 'json',
            type: "GET",
            quietMillis: 250, // Retard pour réduire la charge sur le serveur
            data: function (params) {
                return {
                    q: params || "", // Envoie le terme de recherche ou une chaîne vide
                };
            },
            results: function (data) {
                return {results: data};
            },
        },
        cache: true,
        placeholder: 'Rechercher un imprimeur...',
        minimumInputLength: 1,
    });
}

// Charger les relations existantes
function loadExistingRelations(personId) {
    const patentStruct = Array.from(
        document.querySelectorAll("[id^='patents-'][id$='-id']")
    ).reduce((acc, container) => {
        acc[container.value] = container.id.split("-")[1];
        return acc;
    }, {});
    $.ajax({
        url: `/dil/dil/admin/person/get_patent_relations/${personId}`,
        type: "GET",
        dataType: "json",
        success: function (groupedRelations) {
            if (Object.keys(groupedRelations).length !== 0) {
                Object.entries(groupedRelations).forEach(([pid, relations]) => {
                        // test if relations is empty
                        if (relations.length !== 0) {
                            // build relation rows associated with the patent
                            let containerId = `#patents-${patentStruct[pid]}-relation-container`;
                            let container = document.querySelector(`${containerId}`);
                            if (container) {
                                relations.forEach(relation => addRelationRowFromData(container, relation, patentStruct[pid]));
                                // Vérifie si un bouton d'ajout existe déjà pour ce conteneur
                                if (!document.querySelector(`#${container.id} ~ .add-relation-button`)) {
                                    // Crée et ajoute le bouton "plus"
                                    const addButton = createButton("+", ["btn", "btn-primary", "mb-2"]);
                                    addButton.classList.add("add-relation-button");
                                    container.parentElement.appendChild(addButton);

                                    // Événement pour ajouter une nouvelle relation
                                    addButton.addEventListener("click", () => addRelationRow(container, addButton, patentStruct[pid]));
                                }
                            }
                        } else {
                            // build place to add a relation
                            let containerId = `#patents-${patentStruct[pid]}-relation-container`;
                            let container = document.querySelector(`${containerId}`);
                            if (container) {
                                // Vérifie si un bouton d'ajout existe déjà pour ce conteneur
                                if (!document.querySelector(`#${container.id} ~ .add-relation-button`)) {
                                    // Crée et ajoute le bouton "plus"
                                    const addButton = createButton("+", ["btn", "btn-primary", "mb-2"]);
                                    addButton.classList.add("add-relation-button");
                                    container.parentElement.appendChild(addButton);

                                    // Événement pour ajouter une nouvelle relation
                                    addButton.addEventListener("click", () => addRelationRow(container, addButton, patentStruct[pid]));
                                }
                            }
                        }
                    }
                )
                ;
            }
        }
        ,
        error: function (error) {
            console.error("Erreur lors du chargement des relations :", error);
        }
    });
}

// Ajouter une ligne à partir des données existantes
function addRelationRowFromData(container, relationData, patentId) {
    const row = document.createElement("div");
    row.classList.add("relation-row", "mb-3", "d-flex", "align-items-center");

    const printerSelect = document.createElement("input");
    printerSelect.name = `dynamic_printers[${patentId}][]`;
    printerSelect.classList.add("form-control", "mr-2", "dynamic-printers");


    const typeOptions = [
        {value: "PARTNER", label: "Associé"},
        {value: "SPONSOR", label: "Parrain"},
        {value: "SUCCESSOR", label: "Successeur"},
        {value: "PREDECESSOR", label: "Prédécesseur"},
    ];
    var defaultValue = {value: "PREDECESSOR", label: "Prédécesseur"};


    // Trouver l'option correspondante dans typeOptions
    const matchedOption = typeOptions.find(option => option.label.toLowerCase() === relationData.relation_type.toLowerCase());

    // Si aucune correspondance trouvée, utiliser la valeur par défaut
    const selectedValue = matchedOption || defaultValue;
    const typeSelect = createSelect(`dynamic_relation_types[${patentId}][]`, typeOptions, selectedValue);


    const removeButton = createButton("x", ["btn", "btn-danger", "ml-2"]);
    removeButton.addEventListener("click", () => row.remove());

    row.appendChild(printerSelect);
    row.appendChild(typeSelect);
    row.appendChild(removeButton);

    //container.appendChild(row)
    container.parentNode.appendChild(row)

    $(printerSelect).select2({
            placeholder: 'Rechercher un imprimeur...',
            minimumInputLength: 1,
            initSelection: function (element, callback) {
                var id = $(element).val();
                if (id !== "") {
                    $.ajax("/dil/dil/admin/person/get_printer/" + relationData.person_related_id, {
                        dataType: "json"
                    }).done(function (data) {
                        callback(data);
                    })
                }
            },
            ajax: {
                url: '/dil/dil/admin/person/get_printers', // URL de la route exposée
                dataType: 'json',
                type: "GET",
                quietMillis: 250, // Retard pour réduire la charge sur le serveur
                cache: true,
                data: function (params) {
                    return {
                        q: params || "", // Envoie le terme de recherche ou une chaîne vide
                    };
                },
                results: function (data) {
                    return {results: data};
                },
            },

        },
    );
    $(printerSelect).select2('val', 1);


}


function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}


document.addEventListener("DOMContentLoaded", function () {
    // Trouver tous les conteneurs avec la classe "relation-container-attach"
    const containers = document.querySelectorAll('.relation-container-attach');

    // Réaffecter les IDs pour chaque conteneur
    containers.forEach((container, index) => {
        container.id = `patents-${index}-relation-container`;
    });

    // Charger les relations existantes pour chaque conteneur
    const personId = getUrlParameter('id'); // Récupère l'ID de l'URL
    if (personId) {
        loadExistingRelations(personId);
    } else {
        console.error("Aucun ID trouvé dans l'URL.");
    }
});