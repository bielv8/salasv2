// Main JavaScript file for SENAI classroom management system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize loading states
    initializeLoadingStates();
    
    // Initialize confirmation dialogs
    initializeConfirmationDialogs();
    
    // Initialize auto-save features
    initializeAutoSave();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form enhancements
function initializeFormEnhancements() {
    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
    
    // Real-time form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('input', function(e) {
            validateField(e.target);
        });
    });
}

// Field validation
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const isRequired = field.hasAttribute('required');
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Skip validation for non-required empty fields
    if (!isRequired && value === '') {
        return;
    }
    
    let isValid = true;
    
    // Required field validation
    if (isRequired && value === '') {
        isValid = false;
    }
    
    // Specific field type validations
    switch(fieldType) {
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (value && !emailRegex.test(value)) {
                isValid = false;
            }
            break;
            
        case 'number':
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            const numValue = parseFloat(value);
            
            if (isNaN(numValue)) {
                isValid = false;
            } else {
                if (min && numValue < parseFloat(min)) isValid = false;
                if (max && numValue > parseFloat(max)) isValid = false;
            }
            break;
            
        case 'time':
            const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
            if (value && !timeRegex.test(value)) {
                isValid = false;
            }
            break;
    }
    
    // Apply validation classes
    if (value !== '') {
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    }
    
    return isValid;
}

// Loading states for buttons
function initializeLoadingStates() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                
                // Restore button state if form submission fails
                setTimeout(() => {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
}

// Confirmation dialogs
function initializeConfirmationDialogs() {
    const confirmLinks = document.querySelectorAll('[data-confirm]');
    
    confirmLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Tem certeza que deseja continuar?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Auto-save for forms (draft functionality)
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const formId = form.getAttribute('data-autosave');
        
        // Load saved data
        loadFormData(form, formId);
        
        // Save data on input
        form.addEventListener('input', debounce(function() {
            saveFormData(form, formId);
        }, 1000));
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            clearFormData(formId);
        });
    });
}

// Form data persistence utilities
function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    try {
        localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    } catch (e) {
        console.warn('Unable to save form data to localStorage:', e);
    }
}

function loadFormData(form, formId) {
    try {
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            const data = JSON.parse(savedData);
            
            Object.keys(data).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    if (field.type === 'checkbox') {
                        field.checked = data[key] === 'on';
                    } else {
                        field.value = data[key];
                    }
                }
            });
        }
    } catch (e) {
        console.warn('Unable to load form data from localStorage:', e);
    }
}

function clearFormData(formId) {
    try {
        localStorage.removeItem(`form_${formId}`);
    } catch (e) {
        console.warn('Unable to clear form data from localStorage:', e);
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search and filter functionality
function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterCards(this.value.toLowerCase());
        }, 300));
    }
}

function filterCards(searchTerm) {
    const cards = document.querySelectorAll('.classroom-card');
    
    cards.forEach(card => {
        const cardText = card.textContent.toLowerCase();
        const isVisible = cardText.includes(searchTerm);
        card.style.display = isVisible ? 'block' : 'none';
    });
}

// Modal utilities
function showModal(modalId, title = null, body = null) {
    const modal = document.getElementById(modalId);
    if (modal) {
        if (title) {
            const titleElement = modal.querySelector('.modal-title');
            if (titleElement) titleElement.textContent = title;
        }
        
        if (body) {
            const bodyElement = modal.querySelector('.modal-body');
            if (bodyElement) bodyElement.innerHTML = body;
        }
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            alertDiv.remove();
        }, duration);
    }
}

// Export functions for use in other scripts
window.SenaiClassrooms = {
    showModal,
    showNotification,
    validateField,
    debounce
};

// Print functionality
function printPage() {
    window.print();
}

// Export PDF functionality (if needed)
function exportToPDF(elementId) {
    // This would require a PDF library like jsPDF
    // For now, redirect to server-side PDF generation
    showNotification('Redirecionando para geração de PDF...', 'info');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save forms
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            activeForm.submit();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const bsModal = bootstrap.Modal.getInstance(openModal);
            if (bsModal) bsModal.hide();
        }
    }
});

// Performance monitoring
function logPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
            }, 0);
        });
    }
}

// Initialize performance monitoring in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    logPerformance();
}
