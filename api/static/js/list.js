/*
 * Add List view features on scroll event
 */
document.addEventListener('DOMContentLoaded', function () {
    var paginationMenuBar = document.querySelector('.pagination-menu-bar');
    paginationMenuBar.style.display = 'none';
    window.addEventListener('scroll', function () {
        var nav = document.querySelector('.actions-nav');
        var navOffsetTop = nav.offsetTop; // initial navigation position

        if (window.scrollY > navOffsetTop) { // if scroll position is greater than initial navigation position
            nav.classList.add('fixed-nav');
            /* display pagination menu bar */
            paginationMenuBar.style.display = 'block';

        } else {
            nav.classList.remove('fixed-nav');
            /* hide pagination menu bar */
            paginationMenuBar.style.display = 'none';
        }
    });
});