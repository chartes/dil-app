/**
 * @file Quill editor configuration for the printer form.
 * @description Initializes Quill editors on selected textarea fields, forces
 * pasted content to plain text, synchronizes Quill content with hidden textarea
 * fields, and provides a custom modal for adding, editing, visiting, and removing links.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

/**
 * Quill toolbar configuration used by all editors created by this script.
 *
 * @constant {Array<Array<string|Object>>}
 */
const TOOLBAR_OPTIONS = [
    ['bold', 'italic', 'underline', 'strike', 'link'],
    [{ 'script': 'super' }],
    ['clean'],
];

/**
 * IDs of static textarea fields converted to Quill editors on page load.
 *
 * @constant {string[]}
 */
const TEXTAREA_TO_QUILL = [
    'personal_information',
    'professional_information',
    'comment',
];

/**
 * Quill Clipboard module used as a base class for custom paste behavior.
 *
 * @constant
 */
const Clipboard = Quill.import('modules/clipboard');

/**
 * Quill Delta class used to insert plain text into the editor.
 *
 * @constant
 */
const Delta = Quill.import('delta');

/**
 * Custom Quill clipboard module that pastes content as plain text only.
 *
 * This avoids importing external HTML formatting from copied content and keeps
 * the editor output cleaner and more predictable.
 *
 * @extends Clipboard
 */
class PlainClipboard extends Clipboard {
    /**
     * Capture paste events and insert clipboard text as plain text.
     *
     * If text is selected, the selected content is replaced by the pasted text.
     * The cursor is then moved to the end of the inserted text.
     *
     * @param {ClipboardEvent} e - Paste event captured by Quill.
     * @returns {void}
     */
    onCapturePaste(e) {
        if (e.defaultPrevented || !e.clipboardData) {
            return;
        }

        e.preventDefault();

        const range = this.quill.getSelection(true);
        const text = e.clipboardData.getData('text/plain') || '';

        if (range == null) {
            return;
        }

        if (range.length > 0) {
            this.quill.deleteText(range.index, range.length, 'user');
        }

        this.quill.updateContents(
            new Delta().retain(range.index).insert(text).delete(range.length),
            'user'
        );

        this.quill.setSelection(range.index + text.length, 0, 'silent');
    }
}

/**
 * Register the custom plain-text clipboard module globally for Quill.
 */
Quill.register('modules/clipboard', PlainClipboard, true);

/**
 * Initialize Quill editors and link modal once the document is ready.
 *
 * The initialization covers:
 * - static textarea fields listed in `TEXTAREA_TO_QUILL`;
 * - existing patent reference textarea fields;
 * - newly added patent reference textarea fields after clicking the patent button.
 *
 * @returns {void}
 */
$(document).ready(function () {
    ensureLinkModalExists();

    TEXTAREA_TO_QUILL.forEach(function (textAreaId) {
        createQuillEditor(textAreaId);
    });

    $('textarea[id^="patents-"][id$="-references"]').each(function () {
        if ($(this).siblings('div[id^="quill-wrapper-"]').length === 0) {
            createQuillEditor($(this).attr('id'));
        }
    });

    $('#patents-button').on('click', function () {
        $('textarea[id^="patents-"][id$="-references"]').each(function () {
            if ($(this).siblings('div[id^="quill-wrapper-"]').length === 0) {
                createQuillEditor($(this).attr('id'));
            }
        });
    });
});

/**
 * Create a Quill editor for a textarea field.
 *
 * The original textarea is hidden but remains the source submitted by the form.
 * Its value is synchronized whenever the Quill editor content changes.
 *
 * This function also:
 * - creates a wrapper around the editor;
 * - initializes Quill with the configured toolbar;
 * - manages a custom link modal;
 * - allows editing existing links by clicking them inside the editor.
 *
 * @param {string} textAreaId - ID of the textarea field to convert into a Quill editor.
 * @returns {void}
 */
function createQuillEditor(textAreaId) {
    const commentTextAreaField = $(`#${textAreaId}`);
    const actualTextAreaValue = commentTextAreaField.val();

    /**
     * Resizable wrapper containing the Quill editor.
     *
     * @type {HTMLDivElement}
     */
    const wrapper = document.createElement('div');

    wrapper.setAttribute('id', `quill-wrapper-${textAreaId}`);
    wrapper.classList.add('quill-resizable-wrapper');

    /**
     * DOM container used by Quill as the editor root.
     *
     * @type {HTMLDivElement}
     */
    const div = document.createElement('div');

    div.setAttribute('id', `quill-editor-${textAreaId}`);
    div.classList.add('quill-editor-box');

    wrapper.appendChild(div);
    commentTextAreaField.parent().append(wrapper);

    /**
     * Last known Quill selection range.
     *
     * Used when opening the link modal after toolbar interaction.
     *
     * @type {{index: number, length: number}|null}
     */
    let savedRange = null;

    /**
     * Quill editor instance attached to the current textarea.
     *
     * @type {Quill}
     */
    const quill = new Quill(`#quill-editor-${textAreaId}`, {
        modules: {
            toolbar: {
                container: TOOLBAR_OPTIONS,
                handlers: {
                    /**
                     * Custom handler for the toolbar link button.
                     *
                     * Opens the custom link modal instead of Quill's default prompt.
                     *
                     * @param {boolean|string} value - Toolbar handler value provided by Quill.
                     * @returns {void}
                     */
                    link: function (value) {
                        if (!value) {
                            return;
                        }

                        const range = quill.getSelection() || savedRange;

                        if (!range || range.length === 0) {
                            alert("Sélectionnez d’abord un texte pour ajouter ou modifier un lien.");
                            return;
                        }

                        savedRange = { index: range.index, length: range.length };
                        openLinkModal(quill, savedRange, textAreaId, commentTextAreaField);
                    },
                },
            },
        },
        theme: 'snow',
        placeholder: "Ajouter du texte ici ...",
    });

    quill.root.innerHTML = actualTextAreaValue;

    /**
     * Store the latest selection range for later link editing.
     */
    quill.on('selection-change', function (range) {
        if (range) {
            savedRange = { index: range.index, length: range.length };
        }
    });

    /**
     * Synchronize the hidden textarea with the current Quill HTML content.
     */
    quill.on('text-change', function () {
        commentTextAreaField.val(quill.root.innerHTML);
    });

    /**
     * Open the link modal when clicking an existing link in the editor.
     *
     * The clicked link text is converted into a Quill range so that the link can
     * be edited or removed through the same modal used by the toolbar.
     */
    quill.root.addEventListener('click', function (event) {
        const linkEl = event.target.closest('a');

        if (!linkEl) {
            return;
        }

        event.preventDefault();

        const linkBlot = Quill.find(linkEl, true);

        if (!linkBlot) {
            return;
        }

        const index = quill.getIndex(linkBlot);
        const linkText = (linkEl.innerText || linkEl.textContent || '').replace(/\n/g, ' ');

        const range = {
            index: index,
            length: linkText.length,
        };

        savedRange = range;

        openLinkModal(quill, range, textAreaId, commentTextAreaField);
    });

    commentTextAreaField.hide();
}

/**
 * Ensure that the custom Quill link modal exists in the document.
 *
 * If the modal is already present, the function does nothing. Otherwise, it
 * injects the modal HTML into the document body and attaches all required event
 * listeners for closing, saving, removing, and previewing links.
 *
 * @returns {void}
 */
function ensureLinkModalExists() {
    if (document.getElementById('quill-link-modal-overlay')) {
        return;
    }

    const modalHtml = `
    <div id="quill-link-modal-overlay" class="quill-link-modal-overlay hidden">
        <div class="quill-link-modal" role="dialog" aria-modal="true" aria-labelledby="quill-link-modal-title">
            <div class="quill-link-modal-header">
                <h4 id="quill-link-modal-title">Ajouter un lien</h4>
                <button type="button" class="quill-link-close" id="quill-link-close-btn" aria-label="Fermer">×</button>
            </div>

            <div class="quill-link-modal-body">
                <p id="quill-link-selected-text" class="quill-link-selected-text"></p>

                <label for="quill-link-input" class="quill-link-label">URL</label>
                <input
                    type="url"
                    id="quill-link-input"
                    class="quill-link-input"
                    placeholder="https://exemple.fr"
                    autocomplete="off"
                />

                <div id="quill-link-visit-wrapper" class="quill-link-visit-wrapper hidden">
                    <a
                        id="quill-link-visit"
                        class="quill-link-visit"
                        href="#"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Visiter le lien
                    </a>
                </div>

                <p class="quill-link-help">Exemple : https://exemple.fr</p>
            </div>

            <div class="quill-link-modal-actions">
                <button type="button" id="quill-link-remove-btn" class="quill-link-btn quill-link-btn-danger">
                    Supprimer le lien
                </button>
                <div class="quill-link-modal-actions-right">
                    <button type="button" id="quill-link-cancel-btn" class="quill-link-btn">
                        Annuler
                    </button>
                    <button type="button" id="quill-link-save-btn" class="quill-link-btn quill-link-btn-primary">
                        Enregistrer
                    </button>
                </div>
            </div>
        </div>
    </div>
`;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    document.getElementById('quill-link-cancel-btn').addEventListener('click', closeLinkModal);
    document.getElementById('quill-link-close-btn').addEventListener('click', closeLinkModal);

    document.getElementById('quill-link-input').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveLinkFromModal();
        }

        if (e.key === 'Escape') {
            e.preventDefault();
            closeLinkModal();
        }
    });

    document.getElementById('quill-link-input').addEventListener('input', updateVisitLinkPreview);

    document.getElementById('quill-link-save-btn').addEventListener('click', saveLinkFromModal);
    document.getElementById('quill-link-remove-btn').addEventListener('click', removeLinkFromModal);
}

/**
 * Update the "visit link" preview inside the link modal.
 *
 * The preview is shown only when the input contains a non-empty and valid URL.
 * URLs without a protocol are normalized with `https://`.
 *
 * @returns {void}
 */
function updateVisitLinkPreview() {
    const input = document.getElementById('quill-link-input');
    const visitWrapper = document.getElementById('quill-link-visit-wrapper');
    const visitLink = document.getElementById('quill-link-visit');

    if (!input || !visitWrapper || !visitLink) {
        return;
    }

    const rawUrl = input.value.trim();

    if (!rawUrl) {
        visitWrapper.classList.add('hidden');
        visitLink.setAttribute('href', '#');
        return;
    }

    const normalizedUrl = normalizeUrl(rawUrl);

    if (!isValidUrl(normalizedUrl)) {
        visitWrapper.classList.add('hidden');
        visitLink.setAttribute('href', '#');
        return;
    }

    visitLink.setAttribute('href', normalizedUrl);
    visitWrapper.classList.remove('hidden');
}

/**
 * Open the custom link modal for a selected Quill range.
 *
 * The modal can be used to add a new link or edit an existing one. The selected
 * text is displayed in the modal, and the current link value is prefilled when
 * the selected range already has a link format.
 *
 * Runtime references to the active Quill editor, range, and textarea field are
 * temporarily stored on the modal overlay.
 *
 * @param {Quill} quill - Active Quill editor instance.
 * @param {{index: number, length: number}} range - Selected Quill range.
 * @param {string} textAreaId - ID of the textarea associated with the editor.
 * @param {JQuery} commentTextAreaField - jQuery-wrapped hidden textarea synchronized with Quill.
 * @returns {void}
 */
function openLinkModal(quill, range, textAreaId, commentTextAreaField) {
    const overlay = document.getElementById('quill-link-modal-overlay');
    const title = document.getElementById('quill-link-modal-title');
    const selectedTextBlock = document.getElementById('quill-link-selected-text');
    const input = document.getElementById('quill-link-input');
    const removeBtn = document.getElementById('quill-link-remove-btn');

    const selectedText = quill.getText(range.index, range.length).replace(/\n/g, ' ').trim();
    const formats = quill.getFormat(range.index, range.length);
    const currentLink = typeof formats.link === 'string' ? formats.link : '';

    overlay.classList.remove('hidden');

    if (currentLink) {
        title.textContent = 'Modifier le lien';
        selectedTextBlock.innerHTML = `Modifier le lien pour la mention : <strong>« ${escapeHtml(selectedText)} »</strong>`;
        removeBtn.style.display = 'inline-flex';
    } else {
        title.textContent = 'Ajouter un lien';
        selectedTextBlock.innerHTML = `Ajouter un lien pour la mention : <strong>« ${escapeHtml(selectedText)} »</strong>`;
        removeBtn.style.display = 'none';
    }

    input.value = currentLink || '';
    updateVisitLinkPreview();

    overlay.dataset.editorId = textAreaId;
    overlay._quill = quill;
    overlay._range = { index: range.index, length: range.length };
    overlay._textareaField = commentTextAreaField;

    // Restore the visual selection before editing the link.
    quill.focus();
    quill.setSelection(range.index, range.length, 'silent');

    setTimeout(() => {
        input.focus();
        input.select();
    }, 0);
}

/**
 * Close the custom link modal and reset its temporary state.
 *
 * If an editor and range are attached to the overlay, the function restores
 * focus and selection to the editor.
 *
 * @returns {void}
 */
function closeLinkModal() {
    const overlay = document.getElementById('quill-link-modal-overlay');

    overlay.classList.add('hidden');

    const input = document.getElementById('quill-link-input');
    const visitWrapper = document.getElementById('quill-link-visit-wrapper');
    const visitLink = document.getElementById('quill-link-visit');

    if (input) {
        input.value = '';
    }

    if (visitWrapper) {
        visitWrapper.classList.add('hidden');
    }

    if (visitLink) {
        visitLink.setAttribute('href', '#');
    }

    const quill = overlay._quill;
    const range = overlay._range;

    if (quill && range) {
        quill.focus();
        quill.setSelection(range.index, range.length, 'silent');
    }
}

/**
 * Save the URL entered in the custom link modal.
 *
 * The function validates and normalizes the URL, applies it as a Quill `link`
 * format to the stored range, synchronizes the hidden textarea, and closes
 * the modal.
 *
 * @returns {void}
 */
function saveLinkFromModal() {
    const overlay = document.getElementById('quill-link-modal-overlay');
    const input = document.getElementById('quill-link-input');

    const quill = overlay._quill;
    const range = overlay._range;
    const textareaField = overlay._textareaField;

    if (!quill || !range || range.length === 0) {
        closeLinkModal();
        return;
    }

    const rawUrl = input.value.trim();

    if (!rawUrl) {
        alert("Veuillez saisir une URL.");
        return;
    }

    const normalizedUrl = normalizeUrl(rawUrl);

    if (!isValidUrl(normalizedUrl)) {
        alert("L’URL saisie n’est pas valide.");
        return;
    }

    quill.focus();
    quill.setSelection(range.index, range.length, 'silent');
    quill.formatText(range.index, range.length, 'link', normalizedUrl, 'user');
    quill.setSelection(range.index, range.length, 'silent');

    textareaField.val(quill.root.innerHTML);
    closeLinkModal();
}

/**
 * Remove the link format from the selected range stored in the modal overlay.
 *
 * The function updates the Quill editor, synchronizes the hidden textarea, and
 * closes the modal.
 *
 * @returns {void}
 */
function removeLinkFromModal() {
    const overlay = document.getElementById('quill-link-modal-overlay');
    const quill = overlay._quill;
    const range = overlay._range;
    const textareaField = overlay._textareaField;

    if (!quill || !range || range.length === 0) {
        closeLinkModal();
        return;
    }

    quill.focus();
    quill.setSelection(range.index, range.length, 'silent');
    quill.formatText(range.index, range.length, 'link', false, 'user');
    quill.setSelection(range.index, range.length, 'silent');

    textareaField.val(quill.root.innerHTML);
    closeLinkModal();
}

/**
 * Normalize a URL before validation or insertion into Quill.
 *
 * URLs beginning with `http://`, `https://`, `mailto:`, or `tel:` are returned
 * unchanged. Other values are prefixed with `https://`.
 *
 * @param {string} url - Raw URL entered by the user.
 * @returns {string} Normalized URL.
 */
function normalizeUrl(url) {
    if (/^(https?:\/\/|mailto:|tel:)/i.test(url)) {
        return url;
    }

    return `https://${url}`;
}

/**
 * Check whether a URL is syntactically valid.
 *
 * @param {string} url - URL to validate.
 * @returns {boolean} True if the URL can be parsed by the browser URL API.
 */
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
}

/**
 * Escape HTML-sensitive characters in a string.
 *
 * This is used before injecting selected text into the custom link modal.
 *
 * @param {string} str - Raw string to escape.
 * @returns {string} HTML-escaped string.
 */
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}