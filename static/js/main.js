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
                addQuickReplyButtons();
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
        
        // Don't auto-scroll - let user read and scroll manually
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
    
    function addQuickReplyButtons() {
        // Remove existing quick reply buttons
        const existingButtons = chatContainer.querySelector('.quick-reply-buttons');
        if (existingButtons) {
            existingButtons.remove();
        }
        
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'quick-reply-buttons mt-3 p-3 bg-light rounded';
        buttonsDiv.innerHTML = `
            <h6 class="mb-2 text-muted">💬 Perguntas rápidas:</h6>
            <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-outline-primary btn-sm quick-btn" data-msg="salas livres agora">
                    🏢 Salas livres
                </button>
                <button class="btn btn-outline-success btn-sm quick-btn" data-msg="unity">
                    🎮 Unity
                </button>
                <button class="btn btn-outline-info btn-sm quick-btn" data-msg="capacidade das salas">
                    👥 Capacidade
                </button>
                <button class="btn btn-outline-warning btn-sm quick-btn" data-msg="laboratório de jogos">
                    🎯 Lab Jogos
                </button>
                <button class="btn btn-outline-secondary btn-sm quick-btn" data-msg="blender">
                    🎨 Blender
                </button>
                <button class="btn btn-outline-dark btn-sm quick-btn" data-msg="visual studio">
                    💻 VS Code
                </button>
                <button class="btn btn-outline-primary btn-sm quick-btn" data-msg="sala dev">
                    🚀 Sala DEV
                </button>
                <button class="btn btn-outline-info btn-sm quick-btn" data-msg="quando fecha">
                    ⏰ Horários
                </button>
            </div>
        `;
        
        chatContainer.appendChild(buttonsDiv);
        
        // Add click listeners to quick reply buttons
        const quickBtns = buttonsDiv.querySelectorAll('.quick-btn');
        quickBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const message = this.getAttribute('data-msg');
                chatInput.value = message;
                sendMessage();
            });
        });
        
        // Don't auto-scroll - let user read and scroll manually
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
        // Don't auto-scroll - let user read and scroll manually
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

// PWA Mobile Install Popup
document.addEventListener('DOMContentLoaded', function() {
    initializeMobileInstallPopup();
});

function initializeMobileInstallPopup() {
    const installPopup = document.getElementById('mobileInstallPopup');
    const installBtn = document.getElementById('installAppBtn');
    const dismissBtn = document.getElementById('dismissInstallBtn');
    
    if (!installPopup || !installBtn || !dismissBtn) {
        return; // Elements not found
    }
    
    let deferredPrompt;
    
    // Check if user has dismissed the popup before
    const hasDismissed = localStorage.getItem('pwa_install_dismissed');
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    const isInstalled = window.navigator.standalone === true; // iOS
    
    // Don't show if already installed or dismissed
    if (isStandalone || isInstalled || hasDismissed) {
        return;
    }
    
    // Detect mobile device
    function isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', function(e) {
        // Prevent the default browser install prompt
        e.preventDefault();
        
        // Store the event for later use
        deferredPrompt = e;
        
        // Show popup only on mobile devices
        if (isMobileDevice()) {
            setTimeout(() => {
                installPopup.classList.add('show');
            }, 2000); // Show after 2 seconds
        }
    });
    
    // Install button click handler
    installBtn.addEventListener('click', function() {
        // Hide the popup
        installPopup.classList.remove('show');
        
        if (!deferredPrompt) {
            // If no prompt available, show instructions
            showInstallInstructions();
            return;
        }
        
        // Show the install prompt
        deferredPrompt.prompt();
        
        // Wait for the user's response
        deferredPrompt.userChoice.then(function(choiceResult) {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
                localStorage.setItem('pwa_install_dismissed', 'true');
            } else {
                console.log('User dismissed the install prompt');
            }
            
            // Clear the deferred prompt
            deferredPrompt = null;
        });
    });
    
    // Dismiss button click handler
    dismissBtn.addEventListener('click', function() {
        installPopup.classList.remove('show');
        localStorage.setItem('pwa_install_dismissed', 'true');
    });
    
    // Show install instructions for iOS and other browsers
    function showInstallInstructions() {
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isAndroid = /Android/.test(navigator.userAgent);
        
        let instructions = '';
        
        if (isIOS) {
            instructions = `
                <h5><i class="fab fa-apple me-2"></i>Como instalar no iOS:</h5>
                <ol class="text-start">
                    <li>Toque no botão <strong>Compartilhar</strong> <i class="fas fa-share"></i> no Safari</li>
                    <li>Role para baixo e toque em <strong>"Adicionar à Tela de Início"</strong> <i class="fas fa-plus-square"></i></li>
                    <li>Toque em <strong>"Adicionar"</strong> no canto superior direito</li>
                </ol>
            `;
        } else if (isAndroid) {
            instructions = `
                <h5><i class="fab fa-android me-2"></i>Como instalar no Android:</h5>
                <ol class="text-start">
                    <li>Toque no menu <strong>⋮</strong> no Chrome</li>
                    <li>Toque em <strong>"Adicionar à tela inicial"</strong> <i class="fas fa-mobile-alt"></i></li>
                    <li>Toque em <strong>"Adicionar"</strong></li>
                </ol>
            `;
        } else {
            instructions = `
                <h5><i class="fas fa-mobile-alt me-2"></i>Como instalar:</h5>
                <p class="text-start">
                    No seu navegador, procure pela opção de 
                    <strong>"Adicionar à tela inicial"</strong> ou 
                    <strong>"Instalar aplicativo"</strong> no menu.
                </p>
            `;
        }
        
        const modalBody = `
            <div class="text-center">
                <img src="${window.location.origin}/static/icon-192.png" 
                     alt="SENAI Salas" 
                     style="width: 100px; height: 100px; border-radius: 20px; margin-bottom: 20px;">
                ${instructions}
                <p class="mt-3 text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    Com o app instalado, você terá acesso rápido às salas direto da tela inicial!
                </p>
            </div>
        `;
        
        // Show modal with instructions
        if (window.SenaiClassrooms && window.SenaiClassrooms.showModal) {
            window.SenaiClassrooms.showModal('instructionsModal', '📱 Instalar App SENAI Salas', modalBody);
        } else {
            alert(instructions.replace(/<[^>]*>/g, ''));
        }
    }
    
    // Listen for app installed event
    window.addEventListener('appinstalled', function() {
        console.log('PWA was installed');
        localStorage.setItem('pwa_install_dismissed', 'true');
        
        // Show success notification
        if (window.SenaiClassrooms && window.SenaiClassrooms.showNotification) {
            window.SenaiClassrooms.showNotification(
                '✅ App instalado com sucesso! Você pode acessá-lo pela tela inicial.',
                'success',
                5000
            );
        }
    });
    
    // For iOS: Show popup on mobile even without beforeinstallprompt
    if (isMobileDevice() && /iPad|iPhone|iPod/.test(navigator.userAgent) && !isInstalled) {
        setTimeout(() => {
            installPopup.classList.add('show');
        }, 3000);
        
        // Override install button for iOS
        installBtn.addEventListener('click', function() {
            installPopup.classList.remove('show');
            showInstallInstructions();
        }, { once: true });
    }
}

// Add to global functions
if (window.SenaiClassrooms) {
    window.SenaiClassrooms.initializeMobileInstallPopup = initializeMobileInstallPopup;
}
