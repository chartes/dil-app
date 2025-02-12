// find element img

let img = document.querySelector('img');

// if src endwith unknown.jpg disable div with class image-thumbnail
if (img.src.endsWith('unknown.jpg')) {
    document.querySelector('.image-thumbnail').style.display = 'none';
}