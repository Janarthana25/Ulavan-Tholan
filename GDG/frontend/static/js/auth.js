/**
 * Ulavan Tholan - Auth Guard
 * Protects all pages from unauthenticated access
 * Include this script on every protected page
 */

(function () {
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    const currentPath = window.location.pathname;

    // Pages that don't need login
    const publicPages = ['/', '/index.html', '/login.html'];

    const isPublic = publicPages.some(p => currentPath === p || currentPath.endsWith('index.html') || currentPath.endsWith('login.html'));

    if (!isLoggedIn && !isPublic) {
        window.location.replace('/login.html');
    }

    // Expose logout helper globally
    window.doLogout = function () {
        sessionStorage.clear();
        window.location.replace('/');
    };
})();
