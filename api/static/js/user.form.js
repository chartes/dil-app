/**
 * @file User password form helpers.
 * @description Adds password generation and password visibility controls
 * to the user administration form.
 *
 * The script:
 * - adds a button to generate a strong password through an AJAX endpoint;
 * - fills the password field with the generated password;
 * - displays temporary success or error alerts;
 * - adds a checkbox to show or hide the password value.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

/**
 * Password input field used to store the generated password.
 *
 * @type {HTMLInputElement|null}
 */
const newPasswordField = document.getElementById('new_password_field');

if (newPasswordField) {
    /**
     * Add a button used to generate a new strong password.
     */
    newPasswordField.insertAdjacentHTML('afterend', `
        <br>
        <button type="button"
                class="btn btn-primary mt-2"
                id="generatePasswordBtn">
            Générer un nouveau mot de passe fort
        </button>
    `);

    /**
     * Button triggering password generation.
     *
     * @type {HTMLButtonElement|null}
     */
    const generatePasswordBtn = document.getElementById('generatePasswordBtn');

    if (generatePasswordBtn) {
        /**
         * Generate a new password, fill the password field, and display a temporary alert.
         *
         * @returns {Promise<void>}
         */
        generatePasswordBtn.addEventListener('click', async () => {
            const passwordField = document.getElementById('new_password_field');

            if (!passwordField) {
                return;
            }

            try {
                const newPwd = await generatePassword();

                if (newPwd) {
                    passwordField.value = newPwd;
                    passwordField.setAttribute('value', newPwd);

                    showPasswordFlashMessage(
                        passwordField,
                        'Nouveau mot de passe généré et enregistré avec succès. N\'oubliez pas de le copier avant d\'enregistrer.',
                        'warning'
                    );
                }
            } catch (error) {
                console.error("Erreur lors de la génération du mot de passe :", error);

                showPasswordFlashMessage(
                    passwordField,
                    'Erreur lors de la génération du mot de passe. Veuillez réessayer plus tard.',
                    'danger'
                );
            }
        });
    }

    /**
     * Add a checkbox used to toggle password visibility.
     */
    newPasswordField.insertAdjacentHTML('afterend', `
        <div class="form-check form-switch mt-2" id="showPasswordDiv">
            <input class="form-check-input"
                   type="checkbox"
                   id="showPassword">
            <label class="form-check-label"
                   for="showPassword">
                Voir le mot de passe
            </label>
        </div>
    `);

    /**
     * Checkbox controlling password visibility.
     *
     * @type {HTMLInputElement|null}
     */
    const showPasswordBtn = document.getElementById('showPassword');

    if (showPasswordBtn) {
        showPasswordBtn.addEventListener('change', showPassword);
    }
}

/**
 * Request a newly generated strong password from the server.
 *
 * @returns {Promise<string>} Generated password returned by the server.
 */
function generatePassword() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/dil-db/dil-db/admin/user/generate_password',
            method: 'GET',
            success: function (response) {
                resolve(response.password);
            },
            error: function (error) {
                reject(error);
            },
        });
    });
}

/**
 * Display a temporary flash message below the password field.
 *
 * Any previous password alert is removed before the new one is displayed.
 * The alert is automatically removed after three seconds.
 *
 * @param {HTMLInputElement} passwordField - Password input field after which the alert is inserted.
 * @param {string} message - Alert message displayed to the user.
 * @param {"warning"|"danger"|"success"|"info"} type - Bootstrap alert type.
 * @returns {void}
 */
function showPasswordFlashMessage(passwordField, message, type) {
    const oldFlash = document.querySelector('.new-pwd-alert');

    if (oldFlash) {
        oldFlash.remove();
    }

    const flashMessage = document.createElement('div');

    flashMessage.classList.add('alert', `alert-${type}`, 'mt-2', 'new-pwd-alert');
    flashMessage.textContent = message;

    passwordField.insertAdjacentElement('afterend', flashMessage);

    setTimeout(() => {
        flashMessage.remove();
    }, 3000);
}

/**
 * Toggle password field visibility.
 *
 * When the checkbox is checked, the password field is displayed as plain text.
 * Otherwise, it is displayed as a password input.
 *
 * @returns {void}
 */
function showPassword() {
    const passwordField = document.getElementById('new_password_field');
    const showPasswordCheckbox = document.getElementById('showPassword');

    if (!passwordField || !showPasswordCheckbox) {
        return;
    }

    passwordField.type = showPasswordCheckbox.checked ? 'text' : 'password';
}