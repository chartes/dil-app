/**
 * @file Gallica source form helpers.
 * @description Handles conditional display of image source fields, converts Gallica URLs
 * to IIIF image URLs, and hides unknown placeholder thumbnails.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

document.addEventListener("DOMContentLoaded", function () {
    /**
     * Select field indicating whether the image source is Gallica.
     *
     * @type {HTMLSelectElement|null}
     */
    const gallicaSelect = document.getElementById("is_gallica_source");

    /**
     * Input containing the original reference URL.
     *
     * @type {HTMLInputElement|null}
     */
    const referenceInput = document.getElementById("reference_url");

    /**
     * Input containing the generated IIIF preview URL.
     *
     * @type {HTMLInputElement|null}
     */
    const iiifPreview = document.getElementById("iiif_preview");

    /**
     * Input containing the local image filename.
     *
     * @type {HTMLInputElement|null}
     */
    const imgInput = document.getElementById("img_name");

    /**
     * Form group containing the reference URL input.
     *
     * @type {HTMLElement|null}
     */
    const referenceGroup = referenceInput ? referenceInput.closest(".form-group") : null;

    /**
     * Form group containing the IIIF preview input.
     *
     * @type {HTMLElement|null}
     */
    const iiifGroup = iiifPreview ? iiifPreview.closest(".form-group") : null;

    /**
     * Form group containing the local image filename input.
     *
     * @type {HTMLElement|null}
     */
    const imgGroup = imgInput ? imgInput.closest(".form-group") : null;

    /**
     * Convert a Gallica ARK URL into a IIIF image URL.
     *
     * The function accepts standard Gallica URLs such as:
     * - `https://gallica.bnf.fr/ark:/12148/...`
     * - `https://gallica.bnf.fr/ark:/12148/.../f12.item`
     *
     * Query strings and anchors are removed before parsing.
     * If no folio is found, the function defaults to `f1`.
     *
     * @param {string} url - Gallica URL to convert.
     * @returns {string} Generated IIIF image URL, or an empty string if the URL is invalid.
     */
    function gallicaToIiif(url) {
        if (!url) {
            return "";
        }

        const clean = url.trim().split("?")[0].split("#")[0];

        const match = clean.match(
            /^(https?:\/\/(?:www\.)?gallica\.bnf\.fr\/ark:\/12148\/[^/.?/#]+)(?:\/(f\d+)(?:\.item)?)?/i
        );

        if (!match) {
            return "";
        }

        const baseArkUrl = match[1];
        const folio = match[2] || "f1";

        const arkMatch = baseArkUrl.match(
            /^https?:\/\/(?:www\.)?gallica\.bnf\.fr\/(ark:\/12148\/[^/]+)$/i
        );

        if (!arkMatch) {
            return "";
        }

        return `https://gallica.bnf.fr/iiif/${arkMatch[1]}/${folio}/full/1000,/0/native.jpg`;
    }

    /**
     * Check whether the current source is marked as a Gallica source.
     *
     * @returns {boolean} True if the Gallica source option is selected.
     */
    function isGallicaSelected() {
        return gallicaSelect && gallicaSelect.value === "yes";
    }

    /**
     * Toggle form fields according to the selected source type.
     *
     * When Gallica is selected:
     * - the reference URL field remains visible;
     * - the IIIF preview field is shown and automatically filled;
     * - the local image filename field is hidden.
     *
     * When Gallica is not selected:
     * - the reference URL field remains visible;
     * - the IIIF preview field is hidden and cleared;
     * - the local image filename field is shown.
     *
     * @returns {void}
     */
    function toggleFields() {
        const isGallica = isGallicaSelected();

        if (referenceGroup) {
            referenceGroup.style.display = "";
        }

        if (iiifGroup) {
            iiifGroup.style.display = isGallica ? "" : "none";
        }

        if (imgGroup) {
            imgGroup.style.display = isGallica ? "none" : "";
        }

        if (iiifPreview) {
            iiifPreview.value = isGallica && referenceInput
                ? gallicaToIiif(referenceInput.value)
                : "";
        }
    }

    /**
     * Listen for source type changes and refresh field visibility.
     */
    if (gallicaSelect) {
        gallicaSelect.addEventListener("change", toggleFields);
    }

    /**
     * Listen for reference URL changes and update the IIIF preview URL
     * when the selected source is Gallica.
     */
    if (referenceInput) {
        referenceInput.addEventListener("input", function () {
            if (isGallicaSelected() && iiifPreview) {
                iiifPreview.value = gallicaToIiif(referenceInput.value);
            }
        });
    }

    // Apply the initial field state on page load.
    toggleFields();

    /**
     * Existing thumbnail element, if present in the form.
     *
     * @type {HTMLImageElement|HTMLElement|null}
     */
    const thumb = document.querySelector(".image-thumbnail img, img.image-thumbnail, .image-thumbnail");

    /**
     * Hide the placeholder thumbnail when the current image is unknown.
     */
    if (thumb && thumb.src && thumb.src.endsWith("unknown.jpg")) {
        const wrapper = thumb.closest(".image-thumbnail") || thumb;

        if (wrapper) {
            wrapper.style.display = "none";
        }
    }
});