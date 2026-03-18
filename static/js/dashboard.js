document.addEventListener('DOMContentLoaded', function () {
    var currentPath = window.location.pathname;
    if (currentPath.indexOf('/students/dashboard') !== -1) {
        document.body.classList.add('dashboard-page-loaded');
    }
});
