/**
 * @file Dynamic form logic for DIL DB administration.
 * @description Handles dynamic inline form rows with add/remove behavior.
 *
 * Flask-Admin does not natively support inline models with depth 2.
 * This script creates dynamic inline form rows attached to existing
 * containers inside Flask-Admin inline model views.
 *
 * Script organization:
 * - CONFIGURATION: Defines the configuration for each dynamic form.
 * - UTILS: Provides utility functions for dynamic form creation.
 * - FORM ROW: Creates a single dynamic form row.
 * - INITIALISATION: Initializes dynamic forms and loads existing data.
 * - TRIGGER: Runs initialization on page load.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

// ======================= CONFIGURATION ==========================
(() => {

    "use strict";
/**
 * Base URL for DIL DB administration AJAX endpoints.
 *
 * @constant {string}
 */
const BASE_URL = "/dil-db/dil-db/admin/";

/**
 * @typedef {Object} StaticOption
 * @property {string} value - Option value submitted by the form.
 * @property {string} label - Human-readable option label.
 */

/**
 * @typedef {Object} SelectResult
 * @property {number|string} id - Entity identifier.
 * @property {string} [text] - Select2 display text.
 * @property {string} [name] - Entity display name.
 */

/**
 * @typedef {Object} RelationData
 * @property {number|string} id - Related entity identifier.
 * @property {string} [data] - Relation metadata, such as relation type or date.
 */

/**
 * @typedef {Object} DynamicFormDefaultValues
 * @property {number|string} [selectId] - Default selected entity identifier.
 * @property {StaticOption} [type] - Default selected static relation type.
 * @property {string} [date] - Default date or text value.
 */

/**
 * @typedef {Object} DynamicFormConfig
 * @property {string} containerPrefix - Prefix used to generate dynamic container IDs.
 * @property {string} containerSelectorAttach - CSS selector of containers where rows are attached.
 * @property {function(number|string): string} relationUrl - Function returning the URL used to fetch existing relations.
 * @property {string} ajaxUrl - URL used by Select2 to search related entities.
 * @property {function(number|string): string} fetchSingleUrl - Function returning the URL used to fetch a single selected entity.
 * @property {Object} fieldNames - Functions returning dynamic form field names.
 * @property {function(number|string): string} fieldNames.select - Function returning the select field name.
 * @property {function(number|string): string} [fieldNames.type] - Function returning the relation type field name.
 * @property {function(number|string): string} [fieldNames.date] - Function returning the relation date/text field name.
 * @property {StaticOption[]} [staticOptions] - Static options used by a relation type select field.
 * @property {Object} [toCreate] - Optional configuration for a modal link creating a missing related entity.
 * @property {string} toCreate.url - URL opened in the admin modal.
 * @property {string} toCreate.description - Description displayed next to the creation link.
 */

/**
 * Configuration object for all dynamic forms handled by this script.
 *
 * Each entry defines:
 * - where rows should be inserted;
 * - which AJAX endpoints should be used;
 * - how form field names should be generated;
 * - optional static fields or creation links.
 *
 * @type {Object.<string, DynamicFormConfig>}
 */
const formConfigs = {
    patentRelations: {
        containerPrefix: "patents",
        containerSelectorAttach: ".relation-container-attach",
        relationUrl: (id) => `${BASE_URL}person/get_patent_relations/${id}`,
        ajaxUrl: `${BASE_URL}person/get_printers`,
        fetchSingleUrl: (id) => `${BASE_URL}person/get_printer/${id}`,
        fieldNames: {
            select: (index) => `dynamic_printers[${index}][]`,
            type: (index) => `dynamic_relation_types[${index}][]`,
        },
        staticOptions: [
            { value: "PARTNER", label: "Associé" },
            { value: "SPONSOR", label: "Parrain" },
            { value: "SUCCESSOR", label: "Successeur" },
            { value: "PREDECESSOR", label: "Prédécesseur" },
        ],
    },
    addressesProRelations: {
        containerPrefix: "addresses",
        containerSelectorAttach: ".addresses-container-attach",
        relationUrl: (id) => `${BASE_URL}person/get_pro_addresses/${id}`,
        ajaxUrl: `${BASE_URL}person/get_addresses`,
        fetchSingleUrl: (id) => `${BASE_URL}person/get_address/${id}`,
        toCreate: {
            url: `${BASE_URL}address/new/?url=${BASE_URL}address/`,
            description: "une nouvelle adresse",
        },
        fieldNames: {
            select: (index) => `dynamic_pro_addresses[${index}][]`,
            date: (index) => `dynamic_pro_addresses_date[${index}][]`,
        },
    },
};

// ======================= UTILS ==========================

/**
 * Create a button element with optional CSS classes and ID.
 *
 * @param {string} text - Button text content.
 * @param {string[]} [classes=[]] - CSS classes to add to the button.
 * @param {string|null} [id=null] - Optional button ID.
 * @returns {HTMLButtonElement} Created button element.
 */
function createButton(text, classes = [], id = null) {
    const button = document.createElement("button");

    button.textContent = text;
    button.type = "button";

    if (id) {
        button.id = id;
    }

    classes.forEach(cls => button.classList.add(cls));

    return button;
}

/**
 * Create a select element with options and an optional selected value.
 *
 * Each option can use either:
 * - `value` and `label`;
 * - or `id` and `name`.
 *
 * @param {string} name - Name attribute assigned to the select element.
 * @param {Array<StaticOption|SelectResult>} options - Options used to populate the select element.
 * @param {StaticOption|SelectResult|null} defaultValue - Option selected by default.
 * @param {string[]} [additionalClasses=[]] - Additional CSS classes added to the select element.
 * @returns {HTMLSelectElement} Created select element.
 */
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

/**
 * Read a query parameter from the current page URL.
 *
 * @param {string} name - Query parameter name.
 * @returns {string|null} Query parameter value, or null if absent.
 */
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);

    return urlParams.get(name);
}

// ======================= FORM ROW ==========================

/**
 * Add a dynamic form row to the given inline form container.
 *
 * The row contains:
 * - a Select2 dynamic search field;
 * - optionally, a static relation type select;
 * - optionally, a text/date input;
 * - a remove button.
 *
 * Existing values can be passed through `defaultValues`, which is used when
 * loading already saved relations from the server.
 *
 * @param {DynamicFormConfig} config - Dynamic form configuration.
 * @param {HTMLElement} container - Container associated with the current inline model.
 * @param {HTMLButtonElement} addButton - Button before which the row is inserted.
 * @param {number|string} index - Inline model index used to generate field names.
 * @param {DynamicFormDefaultValues} [defaultValues={}] - Default values used to prefill the row.
 * @returns {void}
 */
function addFormRow(config, container, addButton, index, defaultValues = {}) {
    const row = document.createElement("div");

    row.classList.add("relation-row", "mb-3", "d-flex", "align-items-center");

    // First row field: dynamic Select2 input.
    const selectInput = document.createElement("input");

    selectInput.name = config.fieldNames.select(index);
    selectInput.classList.add("form-control", "mr-2", "dynamic-select2");
    row.appendChild(selectInput);

    // Second row field: static relation type select.
    if (config.staticOptions) {
        const defaultType = defaultValues.type || config.staticOptions[0];

        const typeSelect = createSelect(
            config.fieldNames.type(index),
            config.staticOptions,
            defaultType
        );

        row.appendChild(typeSelect);
    }

    // Optional text/date field.
    if (config.fieldNames.date) {
        const inputDate = document.createElement("input");

        inputDate.type = "text";
        inputDate.name = config.fieldNames.date(index);
        inputDate.placeholder = "Date d'occupation";
        inputDate.value = defaultValues.date || "";
        inputDate.classList.add("form-control", "ml-2");

        row.appendChild(inputDate);
    }

    // Delete button.
    const removeButton = createButton("x", ["btn", "btn-danger", "ml-2"]);

    removeButton.addEventListener("click", () => row.remove());
    row.appendChild(removeButton);

    container.parentNode.insertBefore(row, addButton);

    // Select2 initialization.
    $(selectInput).select2({
        placeholder: 'Rechercher...',
        minimumInputLength: 1,
        initSelection: function (element, callback) {
            if (defaultValues.selectId) {
                $.ajax(config.fetchSingleUrl(defaultValues.selectId), {
                    dataType: "json",
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
                return { results: data };
            },
        },
    });

    $(selectInput).select2('val', 0);

    if (defaultValues.selectId) {
        $.ajax(config.fetchSingleUrl(defaultValues.selectId), {
            dataType: "json",
        }).done(data => {
            const option = new Option(data.text, data.id, true, true);

            $(selectInput).append(option).trigger('change');
        });
    }
}

// ======================= INITIALISATION ==========================

/**
 * Initialize one configured dynamic form type.
 *
 * The function:
 * - finds all configured containers;
 * - assigns generated IDs to them;
 * - appends add-row buttons;
 * - loads existing relations when an entity ID is present in the URL;
 * - optionally appends a modal link to create missing related entities.
 *
 * @param {string} configName - Name of the configuration in `formConfigs`.
 * @returns {void}
 */
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

    if (entityId) {
        loadExistingData(configName, entityId);
    } else {
        console.warn("Aucun ID trouvé dans l'URL.");
    }

    if (config.toCreate) {
        const firstContainer = document.querySelector(config.containerSelectorAttach);

        if (!firstContainer || !firstContainer.parentElement) {
            console.warn(`Conteneur introuvable pour ${configName}: ${config.containerSelectorAttach}`);
        } else {
            const spanCreate = document.createElement("span");

            spanCreate.classList.add("desc-add-model-item");
            spanCreate.innerHTML = `Absent de la liste ? Ajouter ${config.toCreate.description}`;

            const aCreate = document.createElement("a");

            aCreate.classList.add("link-model", "js-open-admin-modal");
            aCreate.href = "#";
            aCreate.dataset.href = config.toCreate.url;
            aCreate.dataset.targetField = "dynamic_pro_addresses";
            aCreate.dataset.modalTitle = "Ajouter une nouvelle adresse au référentiel";

            const spanPlus = document.createElement("span");

            spanPlus.classList.add("plus-icon");
            aCreate.appendChild(spanPlus);
            spanCreate.appendChild(aCreate);

            firstContainer.parentElement.appendChild(spanCreate);
        }
    }
}

/**
 * Load existing relation data for the current entity and rebuild dynamic rows.
 *
 * Existing relations are grouped by patent/address parent ID.
 * The function maps those parent IDs to their inline form index, then inserts
 * rows with the appropriate default selected value and metadata.
 *
 * @param {string} configName - Name of the configuration in `formConfigs`.
 * @param {number|string} entityId - Current entity identifier read from the URL.
 * @returns {void}
 */
function loadExistingData(configName, entityId) {
    const config = formConfigs[configName];

    /**
     * Map of patent IDs to their inline form indexes.
     *
     * @type {Object.<string, string>}
     */
    const patentStruct = Array.from(
        document.querySelectorAll("[id^='patents-'][id$='-id']")
    ).reduce((acc, el) => {
        acc[el.value] = el.id.split("-")[1];

        return acc;
    }, {});

    $.getJSON(config.relationUrl(entityId), groupedRelations => {
        Object.entries(groupedRelations).forEach(([pid, relations]) => {
            const index = patentStruct[pid];
            const container = document.querySelector(`#${config.containerPrefix}-${index}-relation-container`);

            if (!container) {
                return;
            }

            const addButton = document.querySelector(`#${container.id} ~ .add-relation-button`);

            if (relations.length === 0 && !addButton) {
                const newBtn = createButton("+", ["btn", "btn-primary", "mb-2"]);

                newBtn.classList.add("add-relation-button");
                container.parentElement.appendChild(newBtn);
                newBtn.addEventListener("click", () => addFormRow(config, container, newBtn, index));
            }

            relations.forEach(rel => {
                const defaultValues = {
                    selectId: rel.id,
                };

                if (config.staticOptions) {
                    const matched = config.staticOptions.find(
                        opt => opt.label.toLowerCase() === (rel.data || '').toLowerCase()
                    );

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

/**
 * Initialize available dynamic forms on page load.
 *
 * Each form type is initialized only if its corresponding attachment
 * container exists in the current Flask-Admin page.
 *
 * @returns {void}
 */
document.addEventListener("DOMContentLoaded", () => {
    const hasPatentRelations = document.querySelector(".relation-container-attach");
    const hasAddressRelations = document.querySelector(".addresses-container-attach");

    if (hasPatentRelations) {
        initDynamicForm("patentRelations");
    }

    if (hasAddressRelations) {
        initDynamicForm("addressesProRelations");
    }
});
})();