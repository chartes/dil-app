/*
 * Main function to customize specific fields in printer form.
 * DIL DB administration
 * 2025 - L. Terriel (MPN/ENC)
 */

$(document).ready(function () {
    const BASE_URL = "/dil/dil/admin/person/";

    let selectFirstnames = $('.input-select-tag-form-1');

    function configureSelect2(selectElement) {
        selectElement.select2({
            tags: [''],
            tokenSeparators: [','],
            separator: ',',
        });
    }

    configureSelect2(selectFirstnames);
});

// Fonction pour récupérer les détails d'une image
async function fetchImageDetails(imageId, patentID) {
    try {
        const response = await fetch(`/dil/dil/admin/person/get_image_details/?id=${imageId}&patent_id=${patentID}`);
        if (!response.ok) throw new Error(`Erreur ${response.status}: ${response.statusText}`);

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

// Fonction pour ajouter les prévisualisations sous forme de carrousel Slick
function appendSlickCarousel(containerId, images) {
    const container = $(`#${containerId}`);

    // Si le carrousel existe déjà, le détruire pour éviter les doublons
    if (container.hasClass('slick-initialized')) {
        container.slick('unslick');
    }

    container.empty();  // Vider le conteneur avant d'ajouter de nouvelles images

    // Générer les slides du carrousel
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

    // Réinitialiser le carrousel Slick avec les options ajustées
    container.slick({
        slidesToShow: 3,
        slidesToScroll: 1,
        arrows: true,
        dots: true,
        infinite: false,
        prevArrow: '<button type="button" class="slick-prev custom-prev">◀</button>',
        nextArrow: '<button type="button" class="slick-next custom-next">▶</button>',
    });

    // Ajouter les événements de prévisualisation pour chaque image
    images.forEach(image => {
        $(`#preview-btn-${image.id}`).on('click', () => openPreview(image.src, image.label));
        $(`#${containerId} #checkbox-select-${image.id}`).on('change', function () {
            if ($(this).is(':checked')) {
                $(`#${containerId} input[type="checkbox"]`).not(this).prop('checked', false);
            }
        });
    });


}




// Fonction principale de chargement des images et prévisualisation
async function addPreview(event, type = "ele") {
    let selectId = (type === "ele") ? $(event).attr('id') : event.id;
    let imageIds = (type === "ele") ? $(event).select2('val') : $(event).val();

    if (typeof imageIds === "string") imageIds = imageIds.split(",").map(id => id.trim());

    const containerId = `${selectId}-previews`;

    if (!$(`#${containerId}`).length) {
        $(`#${selectId}`).after(`<div id="${containerId}" style="margin-top: 10px;"></div>`);
    }

    let images = [];
    for (let imageId of imageIds) {
        if ($(`#preview-${selectId}-${imageId}`).length) continue;

        let inputId = selectId.replace("-images", "");
        let patentID = $(`#${inputId}-id`).val();
        const imageDetails = await fetchImageDetails(imageId, patentID);

        if (imageDetails) {
            // Tester les URLs
            let imgSrc = await getValidImageSrc(
                imageDetails.img_url,
                imageDetails.img_iiif_url,
                imageDetails.fallback_iiif_url
            );

            let isFallback = (imageDetails.img_url.endsWith('preview-na.png'));

            images.push({
                id: imageDetails.id,
                src: imgSrc,
                label: imageDetails.label,
                selectId,
                is_pinned: imageDetails.is_pinned,
                is_fallback: isFallback
            });
        }
    }

    // Appeler appendSlickCarousel pour reconstruire le carrousel avec les nouvelles images
    if (images.length > 0) {
        appendSlickCarousel(containerId, images);
    } else {
        // destroy the carousel if no images are available
        $(`#${containerId}`).empty();
    }
}

// Fonction pour tester les URLs des images et basculer vers le fallback si nécessaire
function getValidImageSrc(primaryUrl, secondaryUrl, fallbackUrl) {
    return new Promise(resolve => {
        const img = new Image();

        // Test de l'URL principale
        img.src = primaryUrl;
        img.onload = () => resolve(primaryUrl);
        img.onerror = () => {
            // Si l'URL principale échoue, tester la seconde
            img.src = secondaryUrl;
            img.onload = () => resolve(secondaryUrl);
            img.onerror = () => {
                resolve(fallbackUrl);
            };
        };
    });
}




// Fonction d'ouverture de la prévisualisation
function openPreview(url, label) {
    const iframe = $('#imagePreview');
    iframe.attr({'src': url});
    $('#iframeContainer').css('display', 'flex');
    $('#imagePreviewLabel').html(`<span class="label-image-preview">${label}</span>`);
    $('#closePreview').on('click', () => $('#iframeContainer').css('display', 'none'));
}

// Initialisation des champs Select2 et chargement des images sélectionnées
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
