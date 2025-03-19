/*
 * A hook for the inline fields of the Printer form.
 * Save person model and adding a new patent before
 * filled inline patent form.
 *
 */


let patentButton = document.getElementById('patents-button');
patentButton.innerHTML = 'Enregistrer et ajouter un brevet';
/* add class btn btn-primary to the button */
patentButton.classList.add('btn', 'btn-primary');
/* remove btn-default class */
patentButton.classList.remove('btn-default');

patentButton.onclick = function (event) {
    let lastnameInput = document.getElementById('lastname');
    let lastname = lastnameInput.value;
    if (lastname) {
        faForm.addInlineField(this, 'patents');
        const submitButton = document.querySelector('input[name="_continue_editing"]');
        // get the position of page before adding a new patent
        //let position = window.scrollY;
        submitButton.click();
        // scroll to the previous position
        //window.scrollTo(0, position);

    } else {
        alert("Veuillez saisir un nom d'imprimeur/lithographe avant de créer un brevet");
        const submitButton = document.querySelector('input[name="_continue_editing"]');
        submitButton.click();
    }
};
