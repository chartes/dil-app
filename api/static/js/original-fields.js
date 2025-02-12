/*
 * Main function to customize specific fields in printer form.
 * DIL DB administration
 * 2025 - L. Terriel (MPN/ENC)
 *
 * N.B.: This implementation follows e-NDP DB administration ().
 */

$(document).ready(function () {
    const BASE_URL = "/dil/admin/person/"

    let selectFirstnames = $('.input-select-tag-form-1');

    function configureSelect2(selectElement) {
        selectElement.select2({
            tags: [''], // Allow custom tags
            //multiple: true, // Allow multiple selections
            tokenSeparators: [','], // Use semicolon as the token separator,
            separator: ',', // Use semicolon as the separator
        }).on('select2-open', function () {
            // Hide the results container when the select2 dropdown is opened.
            selectElement.data('select2').results.hide();
            // $('.select2-results').css('display', 'none');
        })
    }

    configureSelect2(selectFirstnames);


});


// Fonction pour récupérer les détails d'une image
async function fetchImageDetails(imageId, patentID) {
    try {
        const response = await fetch(`/dil/admin/person/get_image_details/?id=${imageId}&patent_id=${patentID}`);
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

// Fonction pour ajouter les prévisualisations
async function addPreview(event, type = "ele") {

    let selectId = "";
    let imageIds = "";
    if (type === "ele") {
        selectId = $(event).attr('id'); // ID du champ Select2
        imageIds = $(event).select2('val'); // IDs sélectionnés
    } else {
        selectId = event.id; // ID du champ Select2
        imageIds = $(event).val(); // IDs sélectionnés
    }


    // Conversion de imageIds en liste si c'est une chaîne
    if (typeof imageIds === "string") {
        imageIds = imageIds.split(",").map(id => id.trim());
    }

    const containerId = `${selectId}-previews`; // ID du conteneur de prévisualisations

    // Crée un conteneur pour les prévisualisations s'il n'existe pas
    if (!$(`#${containerId}`).length) {
        $(`#${selectId}`).after(`<div id="${containerId}" style="margin-top: 10px;"></div>`);
    }

    if ((imageIds.length >= 1) && (imageIds[0] !== "")) {
        $(`#label-${containerId}`).remove();
        $(`#${containerId}`).append(`<p id="label-${containerId}"><b>Sélectionner une <i>seule</i> image pour l'épingler : </b></p>`);
    }

    if ((imageIds.length === 0)) {
        $(`#label-${containerId}`).remove();
    }

    // Supprime les prévisualisations des images désélectionnées
    $(`#${containerId} [id^="preview-"]`).each(function () {
        const previewId = $(this).attr('id').replace('preview-', '');
        if (!imageIds.includes(previewId)) {
            $(this).remove(); // Supprime la prévisualisation
        }
    });
    // Ajoute des prévisualisations pour les nouvelles images
    const appendImagePreview = (containerId, selectId, imageId, src, label, is_pinned, is_fallback) => {
        const container = $(`#${containerId}`);

        // Générer le HTML de l'image prévisualisée
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

        // Ajouter les événements
        $(`#preview-btn-${imageId}`).on('click', () => openPreview(src, label));

        $(`#${containerId} #checkbox-select-${imageId}`).on('change', function () {
            if ($(this).is(':checked')) {
                $(`#${containerId} input[type="checkbox"]`).not(this).prop('checked', false);
            }
        });
    };


    const loadImage = async (imageId, containerId, selectId) => {


        let inputId = selectId.replace("-images", "");
        // get the value of the input with the id of inputId
        let input = $(`#${inputId}-id`);
        let patentID = input.val();

        const fallbackSrc = "../../../static/icons/preview-na.png"; // Fallback image
        const imageDetails = await fetchImageDetails(imageId, patentID);
        let is_fallback = false;

        if (imageDetails) {
            let {id, img_iiif_url, img_url, label, is_pinned} = imageDetails;
            const img = new Image();
            img.src = img_url;
            // Step 1: Test static_url
            img.onload = () => appendImagePreview(containerId, selectId, id, img_url, label, is_pinned, is_fallback);
            img.onerror = () => {
                // Step 2: If static_url fails, try iiif_url
                img.src = img_iiif_url;
                img.onload = () => appendImagePreview(containerId, selectId, id, img_iiif_url, label, is_pinned, is_fallback);
                img.onerror = () => {
                    // Step 3: If iiif_url fails, fallback to default image
                    is_fallback = true;
                    appendImagePreview(containerId, selectId, id, fallbackSrc, label, is_pinned, is_fallback);
                };
            };


        }
    };

    for (let imageId of imageIds) {
        // Prevents duplicates
        if ($(`#preview-${selectId}-${imageId}`).length) continue;
        await loadImage(imageId, containerId, selectId);
    }

}

function openPreview(url, label) {
    const iframe = $('#imagePreview');
    iframe.attr({'src': url});
    $('#iframeContainer').attr('style', 'display: flex');
    $('#imagePreviewLabel').empty();
    $('#imagePreviewLabel').append(
        `<span class="label-image-preview">${label}</span>`
    );
    $('#closePreview').on('click', function () {
        // Closes the preview on click.
        $('#iframeContainer').attr('style', 'display: none');
    });
}

// Initialisation pour chaque champ Select2 image
// Initialisation pour chaque champ Select2 image
$('.select2-image').each(function () {
    const selectElement = this;

    // Supprime les anciens événements avant d'en ajouter de nouveaux
    /*$(selectElement).off('change').on('change', function (event) {
        addPreview(event.target, "ele");
    });*/

    // Charge les prévisualisations si des valeurs sont déjà présentes
    const selectedValues = $(selectElement).val();


    // Conversion de selectedValues en liste si nécessaire
    const selectedList = typeof selectedValues === "string"
        ? selectedValues.split(",").map(id => id.trim())
        : selectedValues;

    if (selectedList && selectedList.length > 0) {
        addPreview(selectElement, "ids");
    }
});




