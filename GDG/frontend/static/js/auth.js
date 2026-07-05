/**
 * Ulavan Tholan - Auth Guard
 * Works on both localhost and Render deployment
 */

(function () {
    const isLoggedIn  = sessionStorage.getItem('isLoggedIn');
    const currentPath = window.location.pathname;

    // Public pages — no login needed
    const isPublic = ['/', '/index.html', '/login', '/login'].includes(currentPath)
        || currentPath.endsWith('index.html')
        || currentPath.endsWith('login.html')
        || currentPath === '/login';

    if (!isLoggedIn && !isPublic) {
        window.location.replace('/login');
    }

    // Logout helper
    window.doLogout = function () {
        sessionStorage.clear();
        window.location.replace('/');
    };
})();
