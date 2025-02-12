/*
 * Quill editor custom config (person form).
 * 2025 - L. Terriel (ENC)
 *
 * N.B.: adapted from e-NDP implementation
 * use : Select2 v.3.5.3
 * doc : https://select2.github.io/select2/index.html
 */
// Quill editor options for the toolbar
const TOOLBAR_OPTIONS = [
        ['bold', 'italic', 'underline', 'strike', 'script', 'link'],
        [{'script': 'super'}],
        ['clean'],
    ];

// List of textarea id that will be converted to quill editor
const TEXTAREA_TO_QUILL = [
        'personal_information',
        'professional_information',
        'comment',
    ];

$(document).ready(function () {

    TEXTAREA_TO_QUILL.forEach(function (textAreaId) {
        createQuillEditor(textAreaId);
    });

    $('textarea[id^="patents-"][id$="-references"]').each(function () {
            // only convert textarea that are not already converted
            if ($(this).siblings('div').length === 0) {
                createQuillEditor($(this).attr('id'));
            }
        });

    // when doc changes, update the quill editor
    $('#patents-button').on('click', function () {
        // match all textarea with id like "patents-\d+-references" and convert them to quill editor
        $('textarea[id^="patents-"][id$="-references"]').each(function () {
            // only convert textarea that are not already converted
            if ($(this).siblings('div').length === 0) {
                createQuillEditor($(this).attr('id'));
            }
        });
    });
});

function createQuillEditor(textAreaId) {
    let commentTextAreaField = $(`#${textAreaId}`);
    let actualTextAreaValue = commentTextAreaField.val();
    // Convert <br> tags to newline characters
    //var formattedValue = actualTextAreaValue //.replace(/<br\s*\/?>/gi, '\n');

    let div = document.createElement('div');
    div.setAttribute('id', `quill-editor-${textAreaId}`);
    commentTextAreaField.parent().append(div, commentTextAreaField);

    let quill = new Quill(`#quill-editor-${textAreaId}`, {
        modules: {
            toolbar: TOOLBAR_OPTIONS,
            /*keyboard: {
                bindings: {
                    'list autofill': {
                        prefix: /^\s*()$/,
                    }
                }
            }*/
        },
        theme: 'snow',
        placeholder: "Ajouter du texte ici ...",
    });

    // Set the formatted value to the Quill editor
    quill.root.innerHTML = actualTextAreaValue;

    quill.on('text-change', function (delta, oldDelta, source) {
        if (source === 'user') {
            commentTextAreaField.val(quill.root.innerHTML);
            //const semanticHtml = quill.getSemanticHTML();
            //onChange(semanticHtml.replaceAll('<p></p>', '<p><br/></p>'))
        }
    });

    commentTextAreaField.hide();
}

/*

function createQuillEditor(textAreaId) {
        // create a selector where the quill editor will be created
        var commentTextAreaField = $(`#${textAreaId}`);
        // get the actual value of the textarea
        var actualTextAreaValue = commentTextAreaField.val();
        // Create a div element that contains the quill editor
        var div = document.createElement('div');
        // add id to the div element for exemple quill-editor-1 ...
        div.setAttribute('id', `quill-editor-${textAreaId}`);
        // add the div element after the textarea element
        commentTextAreaField.parent().append(div, commentTextAreaField);
        // create the quill editor instance
        var quill = new Quill(`#quill-editor-${textAreaId}`, {
            modules: {
                toolbar: TOOLBAR_OPTIONS,
                // ignore backspace for autolist
                keyboard: {
                    bindings: {
                        'list autofill': {
                            prefix: /^\s*()$/,
                        }
                    }
                }
            },
            theme: 'snow',
            placeholder: "Ajouter du texte ici ...",
        });
        // set value of current element to the quill editor content
        quill.root.innerHTML = actualTextAreaValue;
        // add event listener to quill instance to copy the content of the quill editor to the textarea
        quill.on('text-change', function (delta, oldDelta, source) {
            // set value of current element to the quill editor content
            if (source === 'user') {
                commentTextAreaField.val(quill.root.innerHTML);
            }
        });
        // finally, hide the textarea
        commentTextAreaField.hide();
    }

*/