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
    document.getElementById('signUp-modal').classList.add('hidden');
    backToLoginForm();
    document.body.style.overflow = 'hidden'; // Prevent scrolling bg
}

function closeLoginModal() {
    document.getElementById('login-modal').classList.add('hidden');
    document.body.style.overflow = '';
    document.getElementById('login-form').reset();
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    if (forgotPasswordForm) {
        forgotPasswordForm.reset();
    }
    backToLoginForm();
    document.getElementById('login-success').classList.add('hidden');
}

function openForgotPasswordForm() {
    const loginForm = document.getElementById('login-form');
    const forgotForm = document.getElementById('forgot-password-form');
    const modalTitle = document.querySelector('#login-modal .modal-header h3');
    const modalSubtitle = document.querySelector('#login-modal .modal-header p');

    if (currentLoginType === 'admin') {
        showToast('Forgot password is not available for Admin login.', 'error');
        return;
    }

    if (loginForm && forgotForm) {
        loginForm.classList.add('hidden');
        forgotForm.classList.remove('hidden');
    }

    if (modalTitle) {
        modalTitle.textContent = 'Reset Password';
    }
    if (modalSubtitle) {
        modalSubtitle.textContent = currentLoginType === 'faculty'
            ? 'Verify using Faculty ID and DOB'
            : 'Verify using Student ID and DOB';
    }
}

function backToLoginForm() {
    const loginForm = document.getElementById('login-form');
    const forgotForm = document.getElementById('forgot-password-form');
    const modalTitle = document.querySelector('#login-modal .modal-header h3');
    const modalSubtitle = document.querySelector('#login-modal .modal-header p');

    if (loginForm && forgotForm) {
        forgotForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    }

    if (modalTitle) {
        modalTitle.textContent = 'Welcome Back';
    }
    if (modalSubtitle) {
        modalSubtitle.textContent = 'Login to your account';
    }
}

function switchLoginType(type) {
    currentLoginType = type;
    const studentTab = document.getElementById('login-tab-student');
    const facultyTab = document.getElementById('login-tab-faculty');
    const adminTab = document.getElementById('login-tab-admin');
    const idLabel = document.getElementById('login-id-label');
    const loginIdInput = document.getElementById('login-id');
    const forgotRow = document.getElementById('forgot-password-row');
    const forgotIdLabel = document.getElementById('forgot-id-label');
    const forgotUserIdInput = document.getElementById('forgot-user-id');
    const createAccountRow = document.getElementById('create-account-row');
    
    if (type === 'student') {
        studentTab.classList.add('active');
        facultyTab.classList.remove('active');
        adminTab.classList.remove('active');
        idLabel.textContent = 'Email *';
        if (loginIdInput) {
            loginIdInput.placeholder = 'Enter email';
        }
        if (forgotRow) {
            forgotRow.classList.remove('hidden');
        }
        if (forgotIdLabel) {
            forgotIdLabel.textContent = 'Student ID *';
        }
        if (forgotUserIdInput) {
            forgotUserIdInput.placeholder = 'Enter student ID (e.g. TPI55)';
        }
        if (createAccountRow) {
            createAccountRow.classList.remove('hidden');
        }
    } else if (type === 'faculty') {
        facultyTab.classList.add('active');
        studentTab.classList.remove('active');
        adminTab.classList.remove('active');
        idLabel.textContent = 'Email *';
        if (loginIdInput) {
            loginIdInput.placeholder = 'Enter faculty email';
        }
        if (forgotRow) {
            forgotRow.classList.remove('hidden');
        }
        if (forgotIdLabel) {
            forgotIdLabel.textContent = 'Faculty ID *';
        }
        if (forgotUserIdInput) {
            forgotUserIdInput.placeholder = 'Enter faculty ID (e.g. FAC101)';
        }
        if (createAccountRow) {
            createAccountRow.classList.add('hidden');
        }
    } else {
        adminTab.classList.add('active');
        facultyTab.classList.remove('active');
        studentTab.classList.remove('active');
        idLabel.textContent = 'Admin Username *';
        if (loginIdInput) {
            loginIdInput.placeholder = 'Enter admin username';
        }
        if (forgotRow) {
            forgotRow.classList.add('hidden');
        }
        if (createAccountRow) {
            createAccountRow.classList.add('hidden');
        }
        backToLoginForm();
    }
}

// --- Registration Form ---
function openSignUpModal() {
    document.getElementById('signUp-modal').classList.remove('hidden');
    document.getElementById('login-modal').classList.add('hidden');
    document.body.style.overflow = 'hidden'; // Prevent scrolling bg
}
function closeSignUpModal() {
    document.getElementById('signUp-modal').classList.add('hidden');
    closeLoginModal();
    const signUpForm = document.getElementById('signUp-form');
    if (signUpForm) {
        signUpForm.reset();
    }
    const registrationSuccess = document.getElementById('registration-success');
    if (registrationSuccess) {
        registrationSuccess.classList.add('hidden');
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

function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='));
    if (cookieValue) {
        return decodeURIComponent(cookieValue.split('=')[1]);
    }

    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : '';
}

async function parseApiResponse(response) {
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
        return response.json();
    }

    const text = await response.text();
    return {
        success: false,
        message: text ? `Request failed (${response.status}).` : 'Request failed.',
    };
}

// --- Form Handling ---
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
            }, 1500);
        });
    }

    const forgotPasswordForm = document.getElementById('forgot-password-form');
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const userId = document.getElementById('forgot-user-id').value.trim();
            const dob = document.getElementById('forgot-dob').value;
            const newPassword = document.getElementById('forgot-new-password').value;
            const confirmPassword = document.getElementById('forgot-confirm-password').value;

            if (newPassword !== confirmPassword) {
                showToast('Passwords do not match.', 'error');
                return;
            }

            if (currentLoginType === 'admin') {
                showToast('Forgot password is not available for Admin login.', 'error');
                return;
            }

            const endpoint = currentLoginType === 'faculty'
                ? '/faculty/forgot-password/'
                : '/students/forgot-password/';

            const payload = {
                dob,
                new_password: newPassword,
                confirm_password: confirmPassword,
            };

            if (currentLoginType === 'faculty') {
                payload.faculty_id = userId;
            } else {
                payload.student_id = userId;
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: new URLSearchParams(payload),
                });

                const result = await parseApiResponse(response);

                if (response.ok && result.success) {
                    showToast(result.message || 'Password reset successful.', 'success');
                    const loginIdField = document.getElementById('login-id');
                    if (loginIdField && result.login_id) {
                        loginIdField.value = result.login_id;
                    }
                    forgotPasswordForm.reset();
                    backToLoginForm();
                } else {
                    showToast(result.message || 'Unable to reset password.', 'error');
                }
            } catch (error) {
                showToast('Unable to reset password right now. Please try again.', 'error');
            }
        });
    }

    // Login Form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const loginId = document.getElementById('login-id').value;
            const password = document.getElementById('login-password').value;

            if (currentLoginType === 'admin') {
                try {
                    const response = await fetch('/admin-login/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: new URLSearchParams({
                            username: loginId,
                            password,
                        }),
                    });

                    const result = await parseApiResponse(response);

                    if (response.ok && result.success) {
                        document.getElementById('login-success').classList.remove('hidden');
                        showToast('Welcome, Superuser!', 'success');
                        window.location.href = result.redirect_url || '/admin/';
                    } else {
                        showToast(result.message || 'Invalid superuser credentials.', 'error');
                    }
                } catch (error) {
                    showToast('Unable to login right now. Please try again.', 'error');
                }
                return;
            }

            if (currentLoginType === 'faculty') {
                try {
                    const response = await fetch('/faculty/login/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: new URLSearchParams({
                            email: loginId,
                            password,
                        }),
                    });

                    const result = await parseApiResponse(response);

                    if (response.ok && result.success) {
                        document.getElementById('login-success').classList.remove('hidden');
                        showToast('Faculty login successful!', 'success');
                        window.location.href = result.redirect_url || '/faculty/dashboard/';
                    } else {
                        showToast(result.message || 'Invalid faculty credentials.', 'error');
                    }
                } catch (error) {
                    showToast('Unable to login right now. Please try again.', 'error');
                }
                return;
            }

            try {
                const response = await fetch('/students/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: new URLSearchParams({
                        email: loginId,
                        password,
                    }),
                });

                const result = await parseApiResponse(response);

                if (response.ok && result.success) {
                    document.getElementById('login-success').classList.remove('hidden');
                    showToast('Student login successful!', 'success');
                    window.location.href = result.redirect_url || '/dashboard/';
                } else {
                    showToast(result.message || 'Invalid student credentials.', 'error');
                }
            } catch (error) {
                showToast('Unable to login right now. Please try again.', 'error');
            }
        });
    }

    const signUpForm = document.getElementById('signUp-form');
    if (signUpForm) {
        signUpForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(signUpForm);

            try {
                const response = await fetch('/students/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRFToken(),
                    },
                    body: new URLSearchParams(formData),
                });

                const result = await parseApiResponse(response);

                if (response.ok && result.success) {
                    const successEl = document.getElementById('registration-success');
                    successEl.classList.remove('hidden');
                    successEl.textContent = '✅ Registration successful! Please login with your email and password.';
                    showToast('Registration completed successfully!', 'success');

                    setTimeout(() => {
                        const loginIdField = document.getElementById('login-id');
                        if (loginIdField) {
                            loginIdField.value = result.username || '';
                        }
                        closeSignUpModal();
                        openLoginModal();
                    }, 1200);
                } else {
                    showToast(result.message || 'Registration failed.', 'error');
                }
            } catch (error) {
                showToast('Unable to register right now. Please try again.', 'error');
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