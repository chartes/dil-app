/**
 * @file List view scroll helpers.
 * @description Adds scroll-based behavior to the list view navigation:
 * the actions navigation becomes fixed when the user scrolls past it,
 * and the pagination menu bar is displayed only while the navigation is fixed.
 *
 * @author L. Terriel
 * @copyright 2026 MPN/ENC-PSL
 */

/**
 * Initialize scroll behavior for the list view navigation.
 *
 * On page load, the pagination menu bar is hidden. When the user scrolls
 * past the original position of the actions navigation, the navigation
 * receives the `fixed-nav` CSS class and the pagination menu bar is shown.
 */
document.addEventListener('DOMContentLoaded', function () {
    /**
     * Pagination menu bar displayed when the actions navigation is fixed.
     *
     * @type {HTMLElement|null}
     */
    var paginationMenuBar = document.querySelector('.pagination-menu-bar');

    /**
     * Actions navigation bar that becomes fixed on scroll.
     *
     * @type {HTMLElement|null}
     */
    var nav = document.querySelector('.actions-nav');

    if (!paginationMenuBar || !nav) {
        return;
    }

    paginationMenuBar.style.display = 'none';

    /**
     * Initial vertical offset of the actions navigation.
     *
     * This value is computed once on page load and used as the threshold
     * for switching the navigation into fixed mode.
     *
     * @type {number}
     */
    var navOffsetTop = nav.offsetTop;

    /**
     * Toggle the fixed navigation state according to the current scroll position.
     *
     * @returns {void}
     */
    function toggleFixedNavigation() {
        if (window.scrollY > navOffsetTop) {
            nav.classList.add('fixed-nav');
            paginationMenuBar.style.display = 'block';
        } else {
            nav.classList.remove('fixed-nav');
            paginationMenuBar.style.display = 'none';
        }
    }

    window.addEventListener('scroll', toggleFixedNavigation);
});