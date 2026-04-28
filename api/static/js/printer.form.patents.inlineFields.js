/**
 * @file Printer form inline patent hook.
 * @description Customizes the Flask-Admin inline patent button behavior.
 *
 * This script changes the default patent inline button label and style.
 * When clicked, it checks whether the printer/lithographer lastname has been filled.
 * If a lastname exists, a new inline patent field is added and the form is submitted
 * in "continue editing" mode. If no lastname exists, the form is submitted after
 * displaying an alert, so the user can save the person record before adding patents.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

/**
 * Button used to add an inline patent form to the printer form.
 *
 * @type {HTMLElement|null}
 */
const patentButton = document.getElementById('patents-button');

if (patentButton) {
    patentButton.innerHTML = 'Enregistrer et ajouter un brevet';

    // Apply Bootstrap primary button styling.
    patentButton.classList.add('btn', 'btn-primary');

    // Remove default Bootstrap button styling.
    patentButton.classList.remove('btn-default');

    /**
     * Handle clicks on the inline patent button.
     *
     * If the lastname field is filled, the function adds a new inline patent field
     * and submits the form using the `_continue_editing` action.
     *
     * If the lastname field is empty, the function warns the user and still submits
     * the form using the `_continue_editing` action, allowing the person record to
     * be saved before patent creation.
     *
     * @param {MouseEvent} event - Click event triggered by the patent button.
     * @returns {void}
     */
    patentButton.onclick = function (event) {
        /**
         * Lastname input used to check whether the printer/lithographer
         * has already been identified.
         *
         * @type {HTMLInputElement|null}
         */
        const lastnameInput = document.getElementById('lastname');

        /**
         * Submit button corresponding to Flask-Admin's "continue editing" action.
         *
         * @type {HTMLInputElement|null}
         */
        const submitButton = document.querySelector('input[name="_continue_editing"]');

        const lastname = lastnameInput ? lastnameInput.value : "";

        if (!submitButton) {
            return;
        }

        if (lastname) {
            faForm.addInlineField(this, 'patents');
            submitButton.click();
        } else {
            alert("Veuillez saisir un nom d'imprimeur/lithographe avant de créer un brevet");
            submitButton.click();
        }
    };
}