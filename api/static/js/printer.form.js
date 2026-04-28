/**
 * @file Admin modal helpers specific to printer forms in DIL.
 * @description Provides a reusable modal system for creating related admin
 * entities from the current Flask-Admin form.
 *
 * The script:
 * - opens admin creation forms inside an iframe modal;
 * - appends popup-specific query parameters to the target URL;
 * - closes the modal through button, overlay click, or Escape key;
 * - listens for postMessage success events from the iframe;
 * - displays temporary feedback messages;
 * - enables Bootstrap tooltips.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

(function () {
    /**
     * Modal overlay element containing the iframe.
     *
     * @type {HTMLElement|null}
     */
    const overlay = document.getElementById('adminModalOverlay');

    /**
     * Iframe used to load the related admin creation form.
     *
     * @type {HTMLIFrameElement|null}
     */
    const frame = document.getElementById('adminModalFrame');

    /**
     * Button used to close the admin modal.
     *
     * @type {HTMLButtonElement|null}
     */
    const closeBtn = document.getElementById('adminModalClose');

    /**
     * Modal title element.
     *
     * @type {HTMLElement|null}
     */
    const titleEl = document.getElementById('adminModalTitle');

    if (!overlay || !frame || !closeBtn || !titleEl) {
        return;
    }

    /**
     * Build the popup URL used inside the admin modal iframe.
     *
     * The generated URL receives the following query parameters:
     * - `popup=1`, marking the page as opened in modal mode;
     * - `field_id`, identifying the target field to update;
     * - `modal_title`, storing the title displayed in the modal.
     *
     * @param {string} baseHref - Base admin URL to open inside the modal.
     * @param {string} fieldId - Target field identifier associated with the created element.
     * @param {string} modalTitle - Title displayed in the admin modal.
     * @returns {string} Fully qualified popup URL.
     */
    function buildPopupUrl(baseHref, fieldId, modalTitle) {
        const url = new URL(baseHref, window.location.origin);

        url.searchParams.set('popup', '1');
        url.searchParams.set('field_id', fieldId || '');
        url.searchParams.set('modal_title', modalTitle || 'Ajouter un élément au référentiel');

        return url.toString();
    }

    /**
     * Open the admin modal and load the target URL in the iframe.
     *
     * While the modal is open, body scrolling is disabled.
     *
     * @param {string} url - URL loaded inside the modal iframe.
     * @param {string} title - Title displayed in the modal header.
     * @returns {void}
     */
    function openAdminModal(url, title) {
        frame.src = url;
        titleEl.textContent = title || "Ajouter un élément";
        overlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close the admin modal and reset its iframe.
     *
     * The iframe source is reset to `about:blank` to stop any active page state,
     * and body scrolling is restored.
     *
     * @returns {void}
     */
    function closeAdminModal() {
        frame.src = 'about:blank';
        overlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    /**
     * Display a temporary feedback message above or near the admin modal.
     *
     * The message is automatically removed after four seconds.
     *
     * @param {string} message - HTML message displayed to the user.
     * @param {"success"|"warning"} [level="success"] - Feedback level used to choose the Bootstrap alert class.
     * @returns {void}
     */
    function showModalFeedback(message, level = 'success') {
        const container = document.getElementById('adminModalFeedback');

        if (!container) {
            return;
        }

        const alert = document.createElement('div');

        alert.className = `alert alert-${level === 'warning' ? 'warning' : 'success'}`;
        alert.style.minWidth = '320px';
        alert.style.marginBottom = '10px';
        alert.style.padding = '12px 14px';
        alert.innerHTML = message;

        container.appendChild(alert);

        setTimeout(() => {
            alert.remove();
        }, 4000);
    }

    /**
     * Open the admin modal when clicking an element marked with `.js-open-admin-modal`.
     *
     * Expected data attributes:
     * - `data-href`: target admin URL;
     * - `data-target-field`: optional target field identifier;
     * - `data-modal-title`: optional modal title.
     */
    $(document).on('click', '.js-open-admin-modal', function (event) {
        event.preventDefault();

        const rawHref = $(this).data('href');
        const targetField = $(this).data('target-field') || '';
        const modalTitle = $(this).data('modal-title') || "Ajouter un élément au référentiel";
        const popupUrl = buildPopupUrl(rawHref, targetField, modalTitle);

        openAdminModal(popupUrl, modalTitle);
    });

    /**
     * Close the modal when clicking the close button.
     */
    closeBtn.addEventListener('click', closeAdminModal);

    /**
     * Close the modal when clicking outside the modal content.
     */
    overlay.addEventListener('click', function (event) {
        if (event.target === overlay) {
            closeAdminModal();
        }
    });

    /**
     * Close the modal when pressing the Escape key.
     */
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && overlay.style.display !== 'none') {
            closeAdminModal();
        }
    });

    /**
     * Handle successful creation messages sent by the iframe.
     *
     * The iframe is expected to send a same-origin `postMessage` payload with:
     * `{ type: "admin:create-related-success", message?: string }`.
     */
    window.addEventListener('message', function (event) {
        if (event.origin !== window.location.origin) {
            return;
        }

        const payload = event.data || {};

        if (payload.type !== 'admin:create-related-success') {
            return;
        }

        showModalFeedback(
            payload.message || "L’élément a bien été ajouté au référentiel.",
            'success'
        );

        closeAdminModal();
    });
})();

/**
 * Enable Bootstrap tooltips for elements declaring `data-toggle="tooltip"`.
 *
 * @returns {void}
 */
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});