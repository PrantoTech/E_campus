function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('active');
}

function closeMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.remove('active');
}

const gallerySectionIds = [
    'mainBuilding',
    'scienceLab',
    'computerLab',
    'library',
    'workshop',
    'sportsGround',
    'convocation',
    'sportsDay',
    'techFest',
    'culturalNight',
];

function highlightActiveLinks(sectionId) {
    const sectionLinks = document.querySelectorAll('[data-gallery-section]');
    sectionLinks.forEach((link) => {
        const isActive = link.getAttribute('data-gallery-section') === sectionId;
        link.classList.toggle('active', isActive);
    });
}

function showGallerySection(sectionId) {
    const validSectionId = gallerySectionIds.includes(sectionId) ? sectionId : 'mainBuilding';

    gallerySectionIds.forEach((id) => {
        const section = document.getElementById(id);
        if (!section) {
            return;
        }

        if (id === validSectionId) {
            section.classList.remove('hidden');
        } else {
            section.classList.add('hidden');
        }
    });

    highlightActiveLinks(validSectionId);

    const activeSection = document.getElementById(validSectionId);
    if (!activeSection) {
        return;
    }

    const cards = activeSection.querySelectorAll('.gallery-card');
    cards.forEach((card, index) => {
        card.style.animation = 'none';
        card.offsetHeight;
        card.style.animation = `cardRise 0.5s ease forwards`;
        card.style.animationDelay = `${index * 0.06}s`;
    });
}

function initializeLightbox() {
    const galleryImages = document.querySelectorAll('.gallery-card img');
    if (!galleryImages.length) {
        return;
    }

    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';

    const lightboxImage = document.createElement('img');
    lightboxImage.alt = 'Gallery preview image';

    const closeButton = document.createElement('button');
    closeButton.className = 'lightbox-close';
    closeButton.type = 'button';
    closeButton.setAttribute('aria-label', 'Close preview');
    closeButton.textContent = 'x';

    lightbox.appendChild(lightboxImage);
    lightbox.appendChild(closeButton);
    document.body.appendChild(lightbox);

    const closeLightbox = () => {
        lightbox.classList.remove('open');
        document.body.style.overflow = '';
    };

    galleryImages.forEach((image) => {
        image.addEventListener('click', () => {
            lightboxImage.src = image.src;
            lightboxImage.alt = image.alt || 'Gallery preview image';
            lightbox.classList.add('open');
            document.body.style.overflow = 'hidden';
        });
    });

    closeButton.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (event) => {
        if (event.target === lightbox) {
            closeLightbox();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && lightbox.classList.contains('open')) {
            closeLightbox();
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const queryParams = new URLSearchParams(window.location.search);
    const initialSection = queryParams.get('section') || 'mainBuilding';
    showGallerySection(initialSection);

    const sectionLinks = document.querySelectorAll('[data-gallery-section]');
    sectionLinks.forEach((link) => {
        link.addEventListener('click', (event) => {
            event.preventDefault();
            const sectionId = link.getAttribute('data-gallery-section') || 'mainBuilding';
            showGallerySection(sectionId);
            window.history.replaceState({}, '', `?section=${sectionId}`);
            closeMobileMenu();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    initializeLightbox();
});