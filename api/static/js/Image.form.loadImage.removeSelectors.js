/**
 * @file Flask-Admin form action cleanup.
 * @description Removes selected default Flask-Admin submit buttons from the form.
 *
 * This script hides form actions that are not needed in the current admin view:
 * - `_add_another`
 * - `_continue_editing`
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

/**
 * Remove unnecessary Flask-Admin form action buttons once the DOM is loaded.
 *
 * @returns {void}
 */
document.addEventListener("DOMContentLoaded", function () {
    /**
     * Default Flask-Admin button used to save the current object and add another one.
     *
     * @type {HTMLInputElement|null}
     */
    const addAnother = document.querySelector('input[name="_add_another"]');

    /**
     * Default Flask-Admin button used to save the current object and continue editing it.
     *
     * @type {HTMLInputElement|null}
     */
    const continueEditing = document.querySelector('input[name="_continue_editing"]');

    if (addAnother) {
        addAnother.remove();
    }

    if (continueEditing) {
        continueEditing.remove();
    }
});