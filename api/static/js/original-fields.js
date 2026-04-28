/**
 * @file Main functions to customize specific fields in the printer form.
 * @description DIL DB administration helpers for Select2 fields, image previews,
 * pinned-image selection, and preview modal handling.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 *
 * @note This implementation follows e-NDP DB administration.
 */

/**
 * Base URL for DIL DB person administration AJAX endpoints.
 *
 * @constant {string}
 */
const BASE_URL = "/dil-db/dil-db/admin/person/";

/**
 * @typedef {Object} ImageDetails
 * @property {number|string} id - Image identifier.
 * @property {string} img_iiif_url - IIIF image URL.
 * @property {string} img_url - Static image URL.
 * @property {string} label - Human-readable image label.
 * @property {boolean} is_pinned - Whether the image is currently pinned.
 */

$(document).ready(function () {
    /**
     * Firstname Select2 field supporting custom comma-separated tags.
     *
     * @type {JQuery}
     */
    const selectFirstnames = $('.input-select-tag-form-1');

    /**
     * Configure a Select2 field with tag support and comma-separated values.
     *
     * The Select2 results container is hidden when the dropdown opens,
     * so the field behaves mainly as a tag input.
     *
     * @param {JQuery} selectElement - jQuery-wrapped select element to configure.
     * @returns {void}
     */
    function configureSelect2(selectElement) {
        selectElement.select2({
            tags: [''], // Allow custom tags.
            tokenSeparators: [','], // Use comma as the token separator.
            separator: ',', // Use comma as the value separator.
        }).on('select2-open', function () {
            // Hide the results container when the Select2 dropdown is opened.
            selectElement.data('select2').results.hide();
        });
    }

    configureSelect2(selectFirstnames);
});

/**
 * Retrieve image details from the server.
 *
 * @param {number|string} imageId - Identifier of the image to retrieve.
 * @param {number|string} patentID - Identifier of the related patent or person record.
 * @returns {Promise<ImageDetails|null>} Image details, or null if the request fails or returns an error.
 */
async function fetchImageDetails(imageId, patentID) {
    try {
        const response = await fetch(`${BASE_URL}get_image_details/?id=${imageId}&patent_id=${patentID}`);

        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return null;
        }

        return data;
    } catch (error) {
        console.error("Erreur lors de la récupération des détails de l'image :", error);
        return null;
    }
}

/**
 * Load selected image previews for a Select2 image field.
 *
 * The function:
 * - normalizes selected image IDs;
 * - creates the preview container if needed;
 * - adds or removes the pinned-image instruction label;
 * - removes previews for deselected images;
 * - loads new image previews;
 * - lets the user select only one pinned image.
 *
 * @param {HTMLElement|JQuery} event - Select2 field or DOM element containing selected image IDs.
 * @param {string} [type="ele"] - Input mode. Use `"ele"` for Select2 event mode, otherwise direct element mode.
 * @returns {Promise<void>}
 */
async function addPreview(event, type = "ele") {
    let selectId = "";
    let imageIds = "";

    if (type === "ele") {
        selectId = $(event).attr('id');
        imageIds = $(event).select2('val');
    } else {
        selectId = event.id;
        imageIds = $(event).val();
    }

    // Convert imageIds to a list if it is a string.
    if (typeof imageIds === "string") {
        imageIds = imageIds
            .split(",")
            .map(id => id.trim());
    }

    const containerId = `${selectId}-previews`;

    // Create a preview container if it does not already exist.
    if (!$(`#${containerId}`).length) {
        $(`#${selectId}`).after(`<div id="${containerId}" style="margin-top: 10px;"></div>`);
    }

    if ((imageIds.length >= 1) && (imageIds[0] !== "")) {
        $(`#label-${containerId}`).remove();
        $(`#${containerId}`).append(
            `<p id="label-${containerId}"><b>Sélectionner une <i>seule</i> image pour l'épingler : </b></p>`
        );
    }

    if (imageIds.length === 0) {
        $(`#label-${containerId}`).remove();
    }

    // Remove previews for deselected images.
    $(`#${containerId} [id^="preview-"]`).each(function () {
        const previewId = $(this).attr('id').replace('preview-', '');

        if (!imageIds.includes(previewId)) {
            $(this).remove();
        }
    });

    /**
     * Append a single image preview block to the preview container.
     *
     * Each preview contains:
     * - an image that opens the preview modal on click;
     * - a checkbox used to pin the image;
     * - logic ensuring that only one image can be pinned.
     *
     * @param {string} containerId - ID of the preview container.
     * @param {string} selectId - ID of the related Select2 field.
     * @param {number|string} imageId - Image identifier.
     * @param {string} src - Image source URL.
     * @param {string} label - Image label used for alt, title, and preview display.
     * @param {boolean} is_pinned - Whether the image is currently pinned.
     * @param {boolean} is_fallback - Whether the preview uses the fallback image.
     * @returns {void}
     */
    const appendImagePreview = (containerId, selectId, imageId, src, label, is_pinned, is_fallback) => {
        const container = $(`#${containerId}`);

        const imageHTML = `
        <div id="preview-${selectId}-${imageId}" style="margin: 10px; display: inline-block; text-align: center;">
            <img id="preview-btn-${imageId}" src="${src}" alt="${label}" 
                 style="width: 150px; height: 150px; object-fit: cover; cursor: pointer;" title="${label}">
                <div style="position: relative; cursor: pointer;">
                    <input 
                        type="checkbox" 
                        id="checkbox-select-${imageId}" 
                        name="${selectId}-pinned-image" 
                        value="${imageId}" 
                        title="Sélectionner cette image comme image principale"
                        ${is_pinned ? 'checked' : ''}
                        ${is_fallback ? 'disabled' : ''}>
                </div>
        </div>
    `;

        container.append(imageHTML);

        // Open the image preview modal on click.
        $(`#preview-btn-${imageId}`).on('click', () => openPreview(src, label));

        // Ensure that only one image can be pinned at a time.
        $(`#${containerId} #checkbox-select-${imageId}`).on('change', function () {
            if ($(this).is(':checked')) {
                $(`#${containerId} input[type="checkbox"]`).not(this).prop('checked', false);
            }
        });
    };

    /**
     * Load image details and append the best available preview source.
     *
     * The function first tries the static image URL. If it fails, it tries
     * the IIIF URL. If both fail, it displays a fallback placeholder image
     * and disables the pinned-image checkbox.
     *
     * @param {number|string} imageId - Image identifier to load.
     * @param {string} containerId - ID of the preview container.
     * @param {string} selectId - ID of the related Select2 field.
     * @returns {Promise<void>}
     */
    const loadImage = async (imageId, containerId, selectId) => {
        const inputId = selectId.replace("-images", "");
        const input = $(`#${inputId}-id`);
        const patentID = input.val();

        const fallbackSrc = "../static/icons/preview-na.png";
        const imageDetails = await fetchImageDetails(imageId, patentID);
        let is_fallback = false;

        if (imageDetails) {
            const {id, img_iiif_url, img_url, label, is_pinned} = imageDetails;
            const img = new Image();

            // Step 1: test static image URL.
            img.src = img_url;

            img.onload = () => appendImagePreview(
                containerId,
                selectId,
                id,
                img_url,
                label,
                is_pinned,
                is_fallback
            );

            img.onerror = () => {
                // Step 2: if static image URL fails, try IIIF URL.
                img.src = img_iiif_url;

                img.onload = () => appendImagePreview(
                    containerId,
                    selectId,
                    id,
                    img_iiif_url,
                    label,
                    is_pinned,
                    is_fallback
                );

                img.onerror = () => {
                    // Step 3: if IIIF URL fails, use fallback placeholder image.
                    is_fallback = true;

                    appendImagePreview(
                        containerId,
                        selectId,
                        id,
                        fallbackSrc,
                        label,
                        is_pinned,
                        is_fallback
                    );
                };
            };
        }
    };

    for (const imageId of imageIds) {
        // Prevent duplicate previews.
        if ($(`#preview-${selectId}-${imageId}`).length) {
            continue;
        }

        await loadImage(imageId, containerId, selectId);
    }
}

/**
 * Open the image preview modal and display the selected image.
 *
 * @param {string} url - Image URL to display in the preview iframe.
 * @param {string} label - Label displayed in the preview modal.
 * @returns {void}
 */
function openPreview(url, label) {
    const iframe = $('#imagePreview');

    iframe.attr({src: url});
    $('#iframeContainer').attr('style', 'display: flex');
    $('#imagePreviewLabel').empty();
    $('#imagePreviewLabel').append(
        `<span class="label-image-preview">${label}</span>`
    );

    $('#closePreview').on('click', function () {
        $('#iframeContainer').attr('style', 'display: none');
    });
}

/**
 * Initialize image Select2 fields and load previews for already selected images.
 *
 * For each `.select2-image` field, the script checks whether values are already
 * present. If so, it immediately loads the corresponding previews.
 *
 * @returns {void}
 */
$('.select2-image').each(function () {
    const selectElement = this;

    const selectedValues = $(selectElement).val();

    const selectedList = typeof selectedValues === "string"
        ? selectedValues.split(",").map(id => id.trim())
        : selectedValues;

    if (selectedList && selectedList.length > 0) {
        addPreview(selectElement, "ids");
    }
});