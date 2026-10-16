/* SHOW DE MENU */
const navMenu = document.getElementById('nav-menu'),
    navToggle = document.getElementById('nav-toggle'),
    navClose = document.getElementById('nav-close'),
    overlay = document.getElementById('nav-overlay');

/* Menu show */
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.add('show-menu');

        if (overlay) {
            overlay.classList.add('active');
        }
    });
}

/* Menu hidden (botão fechar) */
if (navClose) {
    navClose.addEventListener('click', () => {
        navMenu.classList.remove('show-menu');

        if (overlay) {
            overlay.classList.remove('active');
        }
    });
}

/* Fechar ao clicar no overlay */
if (overlay) {
    overlay.addEventListener('click', () => {
        navMenu.classList.remove('show-menu');
        overlay.classList.remove('active');
    });
}