/**
 * @file Main functions to customize specific fields in the printer form.
 * @description DIL DB administration helpers for Select2 fields, image previews,
 * Slick carousels, and pinned image selection.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
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
 * @property {string} label - Human-readable image label.
 * @property {string} img_url - Primary image URL.
 * @property {string} img_iiif_url - Secondary IIIF image URL.
 * @property {string} fallback_iiif_url - Fallback IIIF image URL.
 * @property {boolean} is_pinned - Whether the image is currently pinned.
 */

/**
 * @typedef {Object} PreviewImage
 * @property {number|string} id - Image identifier.
 * @property {string} src - Resolved image source URL.
 * @property {string} label - Image label used for alt, title, and preview display.
 * @property {string} selectId - ID of the related Select2 field.
 * @property {boolean} is_pinned - Whether the image is currently pinned.
 * @property {boolean} is_fallback - Whether the image uses the fallback placeholder.
 */

$(document).ready(function () {
    const selectFirstnames = $('.input-select-tag-form-1');

    /**
     * Configure a Select2 field with tag support and comma-separated values.
     *
     * @param {JQuery} selectElement - jQuery-wrapped select element to configure.
     * @returns {void}
     */
    function configureSelect2(selectElement) {
        selectElement.select2({
            tags: [''],
            tokenSeparators: [','],
            separator: ',',
        });
    }

    configureSelect2(selectFirstnames);
});

/**
 * Retrieve image details from the server using an AJAX request.
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
            return null;
        }

        return data;
    } catch (error) {
        console.error("Erreur lors de la récupération des détails de l'image :", error);
        return null;
    }
}

/**
 * Create and append a Slick carousel to the specified container.
 *
 * Each image is displayed with a checkbox for pinned-image selection.
 * Clicking on an image opens it in the preview panel.
 * If the carousel already exists, it is destroyed and rebuilt to avoid duplicates.
 *
 * @param {string} containerId - ID of the container where the carousel will be appended.
 * @param {PreviewImage[]} images - Images to display in the carousel.
 * @returns {void}
 */
function appendSlickCarousel(containerId, images) {
    const container = $(`#${containerId}`);

    // Si le carrousel existe déjà, le détruire pour éviter les doublons.
    if (container.hasClass('slick-initialized')) {
        container.slick('unslick');
    }

    // Vider le conteneur avant d'ajouter de nouvelles images.
    container.empty();

    // Générer les slides du carrousel.
    let slides = '';

    images.forEach(image => {
        slides += `
            <div class="slick-slide-custom">
                <img id="preview-btn-${image.id}" src="${image.src}" alt="${image.label}" 
                     style="width: 150px; height: 150px; object-fit: cover; cursor: pointer; gap:1px !important;" title="${image.label}">
                <div>
                    <input type="checkbox" id="checkbox-select-${image.id}" name="${image.selectId}-pinned-image"
                           value="${image.id}" ${image.is_pinned ? 'checked' : ''} ${image.is_fallback ? 'disabled' : ''}>
                </div>
            </div>`;
    });

    container.append(slides);

    // Réinitialiser le carrousel Slick avec les options ajustées.
    container.slick({
        slidesToShow: 3,
        slidesToScroll: 1,
        arrows: true,
        dots: true,
        infinite: false,
        prevArrow: '<button type="button" class="slick-prev custom-prev">◀</button>',
        nextArrow: '<button type="button" class="slick-next custom-next">▶</button>',
    });

    // Ajouter les événements de prévisualisation et de sélection pour chaque image.
    images.forEach(image => {
        $(`#preview-btn-${image.id}`).on('click', () => openPreview(image.src, image.label));

        $(`#${containerId} #checkbox-select-${image.id}`).on('change', function () {
            if ($(this).is(':checked')) {
                $(`#${containerId} input[type="checkbox"]`).not(this).prop('checked', false);
            }
        });
    });
}

/**
 * Load selected images, resolve their preview URLs, and display them in a Slick carousel.
 *
 * The function supports two modes:
 * - `"ele"`: the provided argument is treated as an element handled through jQuery and Select2.
 * - any other value: the provided argument is treated as a direct DOM element.
 *
 * @param {HTMLElement|JQuery} event - Select2 field or DOM element containing selected image IDs.
 * @param {string} [type="ele"] - Input mode used to retrieve the select ID and selected image IDs.
 * @returns {Promise<void>}
 */
async function addPreview(event, type = "ele") {
    const selectId = (type === "ele") ? $(event).attr('id') : event.id;
    let imageIds = (type === "ele") ? $(event).select2('val') : $(event).val();

    if (!imageIds) {
        imageIds = [];
    }

    if (typeof imageIds === "string") {
        imageIds = imageIds
            .split(",")
            .map(id => id.trim())
            .filter(Boolean);
    }

    if (!Array.isArray(imageIds)) {
        imageIds = [imageIds].filter(Boolean);
    }

    const containerId = `${selectId}-previews`;

    if (!$(`#${containerId}`).length) {
        $(`#${selectId}`).after(`<div id="${containerId}" style="margin-top: 10px;"></div>`);
    }

    const images = [];

    for (const imageId of imageIds) {
        const inputId = selectId.replace("-images", "");
        const patentID = $(`#${inputId}-id`).val();
        const imageDetails = await fetchImageDetails(imageId, patentID);

        if (imageDetails) {
            const imgSrc = await getValidImageSrc(
                imageDetails.img_url,
                imageDetails.img_iiif_url,
                imageDetails.fallback_iiif_url
            );

            const isFallback = (imageDetails.img_url || '').endsWith('preview-na.png');

            images.push({
                id: imageDetails.id,
                src: imgSrc,
                label: imageDetails.label,
                selectId,
                is_pinned: imageDetails.is_pinned,
                is_fallback: isFallback,
            });
        }
    }

    if (images.length > 0) {
        appendSlickCarousel(containerId, images);
    } else {
        $(`#${containerId}`).empty();
    }
}

/**
 * Resolve a valid image source URL.
 *
 * The function first tests the primary URL. If it fails, it tests the secondary URL.
 * If both URLs fail, it resolves with the fallback URL.
 *
 * @param {string} primaryUrl - Preferred image URL.
 * @param {string} secondaryUrl - Secondary image URL, usually an IIIF URL.
 * @param {string} fallbackUrl - Fallback image URL used when all other URLs fail.
 * @returns {Promise<string>} First valid image URL, or the fallback URL.
 */
function getValidImageSrc(primaryUrl, secondaryUrl, fallbackUrl) {
    return new Promise(resolve => {
        const img = new Image();

        // Test de l'URL principale.
        img.src = primaryUrl;

        img.onload = () => resolve(primaryUrl);

        img.onerror = () => {
            // Si l'URL principale échoue, tester la seconde.
            img.src = secondaryUrl;

            img.onload = () => resolve(secondaryUrl);

            img.onerror = () => {
                resolve(fallbackUrl);
            };
        };
    });
}

/**
 * Open the image preview panel and display the selected image.
 *
 * @param {string} url - Image URL to display in the preview iframe.
 * @param {string} label - Label displayed in the preview panel.
 * @returns {void}
 */
function openPreview(url, label) {
    const iframe = $('#imagePreview');

    iframe.attr({ src: url });
    $('#iframeContainer').css('display', 'flex');
    $('#imagePreviewLabel').html(`<span class="label-image-preview">${label}</span>`);
    $('#closePreview').on('click', () => $('#iframeContainer').css('display', 'none'));
}

/**
 * Initialize image Select2 fields and load previews for already selected images.
 *
 * For each `.select2-image` field, this block checks whether values are already selected.
 * If so, it triggers preview loading immediately.
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