// Global State
let currentLoginType = 'student';

// --- Mobile Menu Functions ---
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('active');
}

function closeMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.remove('active');
}

// --- Gallery Functions ---
function showGallery(type) {
    const campusGallery = document.getElementById('gallery-campus');
    const eventsGallery = document.getElementById('gallery-events');
    const tabCampus = document.getElementById('tab-campus');
    const tabEvents = document.getElementById('tab-events');
    
    // Classes for active vs inactive tabs
    const activeClass = 'btn-primary';
    const inactiveClass = 'btn-secondary';

    if (type === 'campus') {
        campusGallery.classList.remove('hidden');
        eventsGallery.classList.add('hidden');
        
        tabCampus.classList.add(activeClass);
        tabCampus.classList.remove(inactiveClass);
        
        tabEvents.classList.remove(activeClass);
        tabEvents.classList.add(inactiveClass);
    } else {
        campusGallery.classList.add('hidden');
        eventsGallery.classList.remove('hidden');
        
        tabEvents.classList.add(activeClass);
        tabEvents.classList.remove(inactiveClass);
        
        tabCampus.classList.remove(activeClass);
        tabCampus.classList.add(inactiveClass);
    }
}

// --- Login Modal Functions ---
function openLoginModal() {
    document.getElementById('login-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent scrolling bg
}

function closeLoginModal() {
    document.getElementById('login-modal').classList.add('hidden');
    document.body.style.overflow = '';
    document.getElementById('login-form').reset();
    document.getElementById('login-success').classList.add('hidden');
}

function switchLoginType(type) {
    currentLoginType = type;
    const studentTab = document.getElementById('login-tab-student');
    const adminTab = document.getElementById('login-tab-admin');
    const idLabel = document.getElementById('login-id-label');
    
    if (type === 'student') {
        studentTab.classList.add('active');
        adminTab.classList.remove('active');
        idLabel.textContent = 'Student ID *';
    } else {
        adminTab.classList.add('active');
        studentTab.classList.remove('active');
        idLabel.textContent = 'Admin Username *';
    }
}

// --- Toast Notifications ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --- Form Handling (Mocking backend interaction) ---
document.addEventListener('DOMContentLoaded', () => {

    // Contact Form
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = document.getElementById('contact-submit');
            const originalText = btn.innerHTML;
            
            // Simulate loading
            btn.innerHTML = 'Sending...';
            btn.disabled = true;

            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
                
                // Show success
                document.getElementById('contact-success').classList.remove('hidden');
                contactForm.reset();
                showToast('Message sent successfully!', 'success');
                
                // Hide success message after 5s
                setTimeout(() => {
                    document.getElementById('contact-success').classList.add('hidden');
                }, 5000);
            }, 1500); // 1.5s delay
        });
    }

    // Login Form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const loginId = document.getElementById('login-id').value;
            const password = document.getElementById('login-password').value;
            
            // Simple validation logic (Mock)
            let isValid = false;
            if (currentLoginType === 'student' && loginId === 'TPI2024001' && password === 'student123') {
                isValid = true;
            } else if (currentLoginType === 'admin' && loginId === 'admin' && password === 'admin123') {
                isValid = true;
            }
            
            if (isValid) {
                document.getElementById('login-success').classList.remove('hidden');
                showToast(`Welcome, ${currentLoginType === 'admin' ? 'Administrator' : 'Student'}!`, 'success');
                setTimeout(() => closeLoginModal(), 2000);
            } else {
                showToast('Invalid credentials. Check demo info.', 'error');
            }
        });
    }

    // Navbar Scroll Effect
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        }
    });
});