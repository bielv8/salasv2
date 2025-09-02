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

// Virtual Assistant functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeVirtualAssistant();
});

function initializeVirtualAssistant() {
    const assistantBtn = document.getElementById('virtualAssistantBtn');
    const assistantModal = document.getElementById('assistantModal');
    const chatContainer = document.getElementById('chatContainer');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');
    
    if (!assistantBtn || !assistantModal || !chatContainer || !chatInput || !sendBtn) {
        return; // Elements not found, skip initialization
    }
    
    // Show modal when button is clicked
    assistantBtn.addEventListener('click', function() {
        const modal = new bootstrap.Modal(assistantModal);
        modal.show();
    });
    
    // Send message when button is clicked
    sendBtn.addEventListener('click', function() {
        sendMessage();
    });
    
    // Send message when Enter is pressed
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-focus input when modal is shown
    assistantModal.addEventListener('shown.bs.modal', function() {
        chatInput.focus();
        
        // Add click handlers for suggestion buttons
        const suggestionButtons = assistantModal.querySelectorAll('.suggestion-btn');
        suggestionButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const suggestion = this.getAttribute('data-suggestion');
                chatInput.value = suggestion;
                sendMessage();
            });
        });
    });
    
    function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Disable input and button
        chatInput.disabled = true;
        sendBtn.disabled = true;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        chatInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to server
        fetch('/api/virtual-assistant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            hideTypingIndicator();
            
            if (data.error) {
                addMessageToChat('assistant', `❌ Desculpe, ocorreu um erro: ${data.error}`);
            } else {
                addMessageToChat('assistant', data.response);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessageToChat('assistant', '❌ Desculpe, não foi possível processar sua pergunta. Tente novamente.');
        })
        .finally(() => {
            // Re-enable input and button
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        });
    }
    
    function addMessageToChat(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        // Convert markdown-like formatting to HTML
        const formattedMessage = formatMessage(message);
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                ${formattedMessage}
            </div>
        `;
        
        // Insert before welcome message (if it exists) or at the end
        const welcomeMessage = chatContainer.querySelector('.welcome-message');
        if (welcomeMessage && sender === 'user') {
            // Insert user messages after welcome message
            welcomeMessage.insertAdjacentElement('afterend', messageDiv);
        } else {
            chatContainer.appendChild(messageDiv);
        }
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function formatMessage(message) {
        // Convert markdown-like formatting to HTML
        let formatted = message
            // Convert **bold** to <strong>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Convert bullet points to HTML list
            .replace(/^• (.+)$/gm, '<li>$1</li>')
            // Convert line breaks to <br>
            .replace(/\n/g, '<br>');
        
        // Wrap consecutive <li> tags in <ul>
        formatted = formatted.replace(/(<li>.*?<\/li>(?:\s*<li>.*?<\/li>)*)/gs, '<ul>$1</ul>');
        
        // Handle emojis and icons
        formatted = formatted
            .replace(/🟢/g, '<span class="text-success">🟢</span>')
            .replace(/🔴/g, '<span class="text-danger">🔴</span>')
            .replace(/💻/g, '<span class="text-primary">💻</span>')
            .replace(/👥/g, '<span class="text-info">👥</span>')
            .replace(/📍/g, '<span class="text-warning">📍</span>')
            .replace(/📅/g, '<span class="text-secondary">📅</span>')
            .replace(/🤖/g, '<span class="text-primary">🤖</span>')
            .replace(/🎯/g, '<span class="text-success">🎯</span>')
            .replace(/📊/g, '<span class="text-info">📊</span>');
        
        return formatted;
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'assistant-message typing-message';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-indicator">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
}

// Add virtual assistant to global functions
if (window.SenaiClassrooms) {
    window.SenaiClassrooms.initializeVirtualAssistant = initializeVirtualAssistant;
}
