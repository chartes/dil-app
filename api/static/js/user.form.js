let newPasswordField = document.getElementById('new_password_field');
// disable the new password field but not with the attribute disabled
//newPasswordField.readOnly = true;

// create a btn and add next to password to generate a random password
newPasswordField.insertAdjacentHTML('afterend', `
<br>
        <button type="button"
                class="btn btn-primary mt-2"
                id="generatePasswordBtn">
            Générer un nouveau mot de passe fort
        </button>
    `);

let generatePasswordBtn = document.getElementById('generatePasswordBtn');

generatePasswordBtn.addEventListener('click', async () => {
    let passwordField = document.getElementById('new_password_field');

    try {
        let newPwd = await generatePassword();  // Attendre la réponse AJAX

        if (newPwd) {
            passwordField.value = newPwd;
            // set attribute to password field
            passwordField.setAttribute('value', newPwd);

            // Supprimer l'alerte précédente si elle existe
            let oldFlash = document.querySelector('.new-pwd-alert');
            if (oldFlash) oldFlash.remove();

            // Créer un message flash
            let flashMessage = document.createElement('div');
            flashMessage.classList.add('alert', 'alert-warning', 'mt-2', 'new-pwd-alert');
            flashMessage.textContent = 'Nouveau mot de passe généré et enregistré avec succès. N\'oubliez pas de le copier avant d\'enregistrer.';

            passwordField.insertAdjacentElement('afterend', flashMessage);

            // Supprimer l'alerte après 3 secondes
            setTimeout(() => {
                flashMessage.remove();
            }, 3000);
        }
    } catch (error) {
        console.error("Erreur lors de la génération du mot de passe :", error);

        // Supprimer l'alerte précédente si elle existe
        let oldFlash = document.querySelector('.new-pwd-alert');
        if (oldFlash) oldFlash.remove();

        // Afficher un message d'erreur
        let flashMessage = document.createElement('div');
        flashMessage.classList.add('alert', 'alert-danger', 'mt-2', 'new-pwd-alert');
        flashMessage.textContent = 'Erreur lors de la génération du mot de passe. Veuillez réessayer plus tard.';

        passwordField.insertAdjacentElement('afterend', flashMessage);

        // Supprimer l'alerte après 3 secondes
        setTimeout(() => {
            flashMessage.remove();
        }, 3000);
    }
});

// Fonction pour générer un mot de passe (Promise)
function generatePassword() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '/dil/dil/admin/user/generate_password',
            method: 'GET',
            success: function (response) {
                resolve(response.password);  // Retourne le mot de passe
            },
            error: function (error) {
                reject(error);  // Gère l'erreur
            }
        });
    });
}



// add a checkbox to show password next to the new password field

newPasswordField.insertAdjacentHTML('afterend', `
        <div class="form-check
                    form-switch
                    mt-2" id="showPasswordDiv">
            <input class="form-check-input"
                   type="checkbox"
                   id="showPassword">
            <label class="form-check-label"
                   for="showPassword">
                Voir le mot de passe
            </label>
        </div>
    `);

let showPasswordBtn = document.getElementById('showPassword');
// add css because I want checkbox to be inline
showPasswordBtn.addEventListener('change', showPassword);

// function to show password
function showPassword() {
    let passwordField = document.getElementById('new_password_field');
    let showPassword = document.getElementById('showPassword');
    if (showPassword.checked) {
        passwordField.type = 'text';
    } else {
        passwordField.type = 'password';
    }
}


