/*
*  Dynamic Form Logic
*  -----------------------------------------------------
*  Handles dynamic forms with add/remove rows.
*
*  By default, Flask-admin does not support inline model with depth 2.
*  So, We used this script to create inline form for depth relations attach to a
*  existing container define inside an inline models in flask admin views.
*  -----------------------------------------------------
*  Script organisation :
*  - CONFIGURATION: Define the configuration for each dynamic form.
*  - UTILS: Utility functions for dynamic form.
*  - FORM ROW: Create a single row of dynamic form.
*  - INITIALISATION: Initialisation of dynamic form.
*  - TRIGGER: Trigger the initialisation on page load.
*/

// ======================= CONFIGURATION ==========================
const formConfigs = {
    patentRelations: {
        containerPrefix: "patents",
        containerSelectorAttach: ".relation-container-attach",
        relationUrl: (id) => `/dil/dil/admin/person/get_patent_relations/${id}`,
        ajaxUrl: "/dil/dil/admin/person/get_printers",
        fetchSingleUrl: (id) => `/dil/dil/admin/person/get_printer/${id}`,
        fieldNames: {
            select: (index) => `dynamic_printers[${index}][]`,
            type: (index) => `dynamic_relation_types[${index}][]`
        },
        staticOptions: [
            {value: "PARTNER", label: "Associé"},
            {value: "SPONSOR", label: "Parrain"},
            {value: "SUCCESSOR", label: "Successeur"},
            {value: "PREDECESSOR", label: "Prédécesseur"},
        ]
    },
    addressesProRelations: {
        containerPrefix: "addresses",
        containerSelectorAttach: ".addresses-container-attach",
        relationUrl: (id) => `/dil/dil/admin/person/get_pro_addresses/${id}`,
        ajaxUrl: "/dil/dil/admin/person/get_addresses",
        fetchSingleUrl: (id) => `/dil/dil/admin/person/get_address/${id}`,
        toCreate: {
          url: "/dil/dil/admin/address/new/?url=/dil/dil/admin/address/",
            description: "une nouvelle adresse",
        },
        fieldNames: {
            select: (index) => `dynamic_pro_addresses[${index}][]`,
            date: (index) => `dynamic_pro_addresses_date[${index}][]` // input text
        },
    }
};

// ======================= UTILS ==========================

function createButton(text, classes = [], id = null) {
    const button = document.createElement("button");
    button.textContent = text;
    button.type = "button";
    if (id) button.id = id;
    classes.forEach(cls => button.classList.add(cls));
    return button;
}

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

function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// ======================= FORM ROW ==========================

function addFormRow(config, container, addButton, index, defaultValues = {}) {
    const row = document.createElement("div");
    row.classList.add("relation-row", "mb-3", "d-flex", "align-items-center");

    // First row field
    // === SELECT2 dynamic  ===
    const selectInput = document.createElement("input");
    selectInput.name = config.fieldNames.select(index);
    selectInput.classList.add("form-control", "mr-2", "dynamic-select2");
    row.appendChild(selectInput);

    // Second row field
    // === static type ===
    if (config.staticOptions) {
        const defaultType = defaultValues.type || config.staticOptions[0];
        const typeSelect = createSelect(
            config.fieldNames.type(index),
            config.staticOptions,
            defaultType
        );
        row.appendChild(typeSelect);
    }

    // === text type ===
    // actually is 'date' but in future can be any 'text' from config if a
    // lot of dynamic field is needed in same form!
    if (config.fieldNames.date) {
        const inputDate = document.createElement("input");
        inputDate.type = "text";
        inputDate.name = config.fieldNames.date(index);
        inputDate.placeholder = "Date d'occupation";
        inputDate.value = defaultValues.date || "";
        inputDate.classList.add("form-control", "ml-2");
        row.appendChild(inputDate);
    }

    // === Delete Btn ===
    const removeButton = createButton("x", ["btn", "btn-danger", "ml-2"]);
    removeButton.addEventListener("click", () => row.remove());
    row.appendChild(removeButton);

    container.parentNode.insertBefore(row, addButton);

    // === Select2 initialisation ===
    $(selectInput).select2({
        placeholder: 'Rechercher...',
        minimumInputLength: 1,
        initSelection: function (element, callback) {
            if (defaultValues.selectId) {
                $.ajax(config.fetchSingleUrl(defaultValues.selectId), {
                    dataType: "json"
                }).done(function (data) {
                    callback(data);
                });
            }
        },
        ajax: {
            url: config.ajaxUrl,
            dataType: 'json',
            type: "GET",
            quietMillis: 250,
            cache: true,
            data: function (params) {
                return {
                    q: params || "",
                };
            },
            results: function (data) {
                return {results: data};
            },
        },
    });

    $(selectInput).select2('val', 0);

    if (defaultValues.selectId) {
        $.ajax(config.fetchSingleUrl(defaultValues.selectId), {
            dataType: "json"
        }).done(data => {
            const option = new Option(data.text, data.id, true, true);
            $(selectInput).append(option).trigger('change');
        });
    }
}

// ======================= INITIALISATION ==========================

function initDynamicForm(configName) {
    const config = formConfigs[configName];
    const containers = document.querySelectorAll(config.containerSelectorAttach);

    containers.forEach((container, index) => {
        const containerId = `${config.containerPrefix}-${index}-relation-container`;
        container.id = containerId;

        const addButton = createButton("+", ["btn", "btn-primary", "mb-2"]);
        addButton.classList.add("add-relation-button");
        container.parentElement.appendChild(addButton);
        addButton.addEventListener("click", () => addFormRow(config, container, addButton, index));
    });

    const entityId = getUrlParameter('id');
    if (entityId) loadExistingData(configName, entityId);
    else console.warn("Aucun ID trouvé dans l'URL.");

    if (config.toCreate){
        const spanCreate = document.createElement("span")
        spanCreate.classList.add("desc-add-model-item");
        spanCreate.innerHTML = `Absent de la liste ? Ajouter ${config.toCreate.description}`;
        const aCreate = document.createElement("a");
        aCreate.classList.add("link-model");
        aCreate.href = config.toCreate.url;
        aCreate.target = "_blank";
        spanCreate.appendChild(aCreate);
        const spanPlus = document.createElement("span");
        spanPlus.classList.add("plus-icon");
        aCreate.appendChild(spanPlus);
        let container = document.querySelector(config.containerSelectorAttach);
        container.parentElement.appendChild(spanCreate);
    }
}

function loadExistingData(configName, entityId) {
    const config = formConfigs[configName];
    const patentStruct = Array.from(
        document.querySelectorAll("[id^='patents-'][id$='-id']")
    ).reduce((acc, el) => {
        acc[el.value] = el.id.split("-")[1];
        return acc;
    }, {});

    $.getJSON(config.relationUrl(entityId), groupedRelations => {
        console.log(groupedRelations);
        Object.entries(groupedRelations).forEach(([pid, relations]) => {
            console.log(pid, relations);
            const index = patentStruct[pid];
            const container = document.querySelector(`#${config.containerPrefix}-${index}-relation-container`);
            const addButton = document.querySelector(`#${container.id} ~ .add-relation-button`);

            if (!container) return;

            if (relations.length === 0 && !addButton) {
                const newBtn = createButton("+", ["btn", "btn-primary", "mb-2"]);
                newBtn.classList.add("add-relation-button");
                container.parentElement.appendChild(newBtn);
                newBtn.addEventListener("click", () => addFormRow(config, container, newBtn, index));
            }

            relations.forEach(rel => {
                let defaultValues = {
                    selectId: rel.id
                };

                if (config.staticOptions) {
                    const matched = config.staticOptions.find(opt => opt.label.toLowerCase() === (rel.data || '').toLowerCase());
                    defaultValues.type = matched || config.staticOptions[0];
                } else if (rel.data) {
                    defaultValues.date = rel.data;
                }

                addFormRow(config, container, addButton, index, defaultValues);
            });
        });
    });
}

// ======================= TRIGGER ==========================

document.addEventListener("DOMContentLoaded", () => {
    initDynamicForm("patentRelations");
    initDynamicForm("addressesProRelations");
});
