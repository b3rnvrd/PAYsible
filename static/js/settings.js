// ============================
// Configuration
// ============================
const API_CONFIG = {
    BASE_URL: '/api',
    ENDPOINTS: {
        USER_PROFILE: '/api/users/me/',
        ACCOUNTS: '/api/accounts/',
        ACCOUNT_BALANCE: (id) => `/api/accounts/${id}/balance/`,
        ACCOUNT_DETAIL: (id) => `/api/accounts/${id}/`
    }
};

const STORAGE_KEYS = {
    PREFERENCES: 'paysible_preferences'
};

// ============================
// Gestion de la Navigation
// ============================
class SettingsNavigation {
    constructor() {
        this.navLinks = document.querySelectorAll('.settings-nav .nav-link');
        this.sections = document.querySelectorAll('.settings-section');
        this.init();
        this.handleUrlHash();
    }

    init() {
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e, link));
        });
    }

    handleNavClick(e, link) {
        e.preventDefault();
        
        // Mettre à jour la navigation
        this.navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        // Afficher la section correspondante
        const sectionId = link.getAttribute('data-section');
        this.showSection(sectionId);
    }

    handleUrlHash() {
        // Récupère le hash de l'URL : #profile, #accounts, #app-settings, etc.
        const hash = window.location.hash.replace('#', '');
        
        if (hash) {
            const link = document.querySelector('.settings-nav a[data-section="' + hash + '"]');
            if (link) {
                // On simule un clic sur l'onglet correspondant
                link.click();
            }
        }
    }

    showSection(sectionId) {
        this.sections.forEach(section => section.classList.remove('active'));
        const targetSection = document.getElementById(sectionId);
        
        if (targetSection) {
            targetSection.classList.add('active');
            
            // Charger les données si nécessaire
            if (sectionId === 'accounts') {
                accountsManager.loadAccounts();
            }
        }
    }
}

// ============================
// Gestion du Profil Utilisateur
// ============================
class UserProfileManager {
    constructor() {
        this.form = document.getElementById('profile-form');
        this.alertDiv = document.getElementById('profile-alert');
        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            this.loadProfile();
        }
    }

    async loadProfile() {
        try {
            const response = await fetch(API_CONFIG.ENDPOINTS.USER_PROFILE);
            
            if (response.ok) {
                const user = await response.json();
                this.populateForm(user);
            } else {
                console.error('Erreur lors du chargement du profil');
            }
        } catch (error) {
            console.error('Erreur de connexion:', error);
        }
    }

    populateForm(user) {
        const fields = ['first_name', 'last_name', 'email', 'phone', 'address'];
        
        fields.forEach(field => {
            const input = document.getElementById(field);
            if (input) {
                input.value = user[field] || '';
            }
        });
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = {
            first_name: document.getElementById('first_name').value,
            last_name: document.getElementById('last_name').value,
            phone: document.getElementById('phone').value,
            address: document.getElementById('address').value
        };
        
        try {
            const response = await fetch(API_CONFIG.ENDPOINTS.USER_PROFILE, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                AlertManager.show(this.alertDiv, 'success', 'Profil mis à jour avec succès !');
            } else {
                AlertManager.show(this.alertDiv, 'danger', 'Erreur lors de la mise à jour du profil.');
            }
        } catch (error) {
            AlertManager.show(this.alertDiv, 'danger', 'Erreur de connexion au serveur.');
        }
    }
}

// ============================
// Gestion des Comptes Bancaires
// ============================
class AccountsManager {
    constructor() {
        this.accountsList = document.getElementById('accounts-list');
        this.alertDiv = document.getElementById('accounts-alert');
        this.addModal = document.getElementById('addAccountModal');
        this.editModal = document.getElementById('editAccountModal');
        this.init();
    }

    init() {
        // Bouton de création
        const btnCreate = document.getElementById('btn-create-account');
        if (btnCreate) {
            btnCreate.addEventListener('click', () => this.createAccount());
        }
    }

    async loadAccounts() {
        if (!this.accountsList) return;
        
        this.accountsList.innerHTML = this.getLoadingHTML();
        
        try {
            const response = await fetch(API_CONFIG.ENDPOINTS.ACCOUNTS);
            
            if (response.ok) {
                const accounts = await response.json();
                this.displayAccounts(accounts);
            } else {
                this.accountsList.innerHTML = this.getErrorHTML('Impossible de charger les comptes.');
            }
        } catch (error) {
            this.accountsList.innerHTML = this.getErrorHTML('Erreur de connexion au serveur.');
        }
    }

    displayAccounts(accounts) {
        if (accounts.length === 0) {
            this.accountsList.innerHTML = this.getEmptyStateHTML();
            return;
        }
        
        this.accountsList.innerHTML = accounts.map(account => 
            this.getAccountCardHTML(account)
        ).join('');
        
        // Charger les soldes
        accounts.forEach(account => this.loadAccountBalance(account.id));
    }

    async loadAccountBalance(accountId) {
        try {
            const response = await fetch(API_CONFIG.ENDPOINTS.ACCOUNT_BALANCE(accountId));
            
            if (response.ok) {
                const data = await response.json();
                const balanceElement = document.getElementById(`balance-${accountId}`);
                
                if (balanceElement) {
                    balanceElement.innerHTML = `${(data.balance || 0).toFixed(2)} €`;
                }
            }
        } catch (error) {
            console.error(`Erreur lors du chargement du solde du compte ${accountId}:`, error);
        }
    }

    async createAccount() {
        const form = document.getElementById('add-account-form');
        const formData = new FormData(form);
        
        const data = {
            type: formData.get('type')
        };
        
        if (!data.type) {
            alert('Veuillez sélectionner un type de compte.');
            return;
        }
        
        try {
            const response = await fetch(API_CONFIG.ENDPOINTS.ACCOUNTS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                this.closeModal(this.addModal);
                form.reset();
                this.loadAccounts();
                AlertManager.show(this.alertDiv, 'success', 'Compte créé avec succès !');
            } else {
                alert('Erreur lors de la création du compte.');
            }
        } catch (error) {
            alert('Erreur de connexion au serveur.');
        }
    }

    async deleteAccount(accountId, accountType) {
        const typeLabel = accountType === 'CHECKING' ? 'Courant' : 'Épargne';
        if (!confirm(`Êtes-vous sûr de vouloir clôturer ce compte ${typeLabel} ?`)) {
            return;
        }
        
        try {
            const response = await fetch(API_CONFIG.ENDPOINTS.ACCOUNT_DETAIL(accountId), {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.loadAccounts();
                AlertManager.show(this.alertDiv, 'success', 'Compte clôturé avec succès !');
            } else {
                alert('Erreur lors de la clôture du compte.');
            }
        } catch (error) {
            alert('Erreur de connexion au serveur.');
        }
    }

    closeModal(modal) {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
            bsModal.hide();
        }
    }

    // Templates HTML
    getLoadingHTML() {
        return `
            <div class="col-12 text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
            </div>
        `;
    }

    getErrorHTML(message) {
        return `
            <div class="col-12">
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${message}
                </div>
            </div>
        `;
    }

    getEmptyStateHTML() {
        return `
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> Vous n'avez aucun compte pour le moment. 
                    Créez-en un en cliquant sur "Nouveau Compte".
                </div>
            </div>
        `;
    }

    getAccountCardHTML(account) {
        const typeLabel = account.type === 'CHECKING' ? 'Courant' : 'Épargne';
        const typeClass = account.type === 'CHECKING' ? 'bg-primary' : 'bg-success';
        const createdDate = new Date(account.created_at || Date.now()).toLocaleDateString('fr-FR');
        
        return `
            <div class="col-md-6 mb-3">
                <div class="card account-card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">Compte ${typeLabel}</h6>
                            <span class="account-badge ${typeClass} text-white">
                                ${typeLabel}
                            </span>
                        </div>
                        
                        <div class="iban-display mb-3">
                            ${account.iban || 'IBAN en cours de génération...'}
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted">Solde actuel</small>
                            <div class="balance-amount" id="balance-${account.id}">
                                <span class="spinner-border spinner-border-sm" role="status"></span>
                            </div>
                        </div>
                        
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-outline-danger" 
                                    onclick="accountsManager.deleteAccount(${account.id}, '${account.type}')">
                                <i class="bi bi-trash"></i> Clôturer
                            </button>
                        </div>
                        
                        <small class="text-muted d-block mt-2">
                            <i class="bi bi-calendar"></i> Créé le ${createdDate}
                        </small>
                    </div>
                </div>
            </div>
        `;
    }
}

// ============================
// Gestion des Préférences
// ============================
class PreferencesManager {
    constructor() {
        this.form = document.getElementById('app-settings-form');
        this.alertDiv = document.getElementById('settings-alert');
        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            this.loadPreferences();
        }
    }

    loadPreferences() {
        const saved = localStorage.getItem(STORAGE_KEYS.PREFERENCES);
        
        if (saved) {
            try {
                const preferences = JSON.parse(saved);
                this.populateForm(preferences);
            } catch (error) {
                console.error('Erreur lors du chargement des préférences:', error);
            }
        }
    }

    populateForm(preferences) {
        const fields = {
            notif_transactions: preferences.notif_transactions !== false,
            notif_email: preferences.notif_email !== false,
            currency: preferences.currency || 'EUR',
            language: preferences.language || 'fr'
        };

        Object.entries(fields).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = value;
                } else {
                    element.value = value;
                }
            }
        });
    }

    handleSubmit(e) {
        e.preventDefault();
        
        const preferences = {
            notif_transactions: document.getElementById('notif_transactions').checked,
            notif_email: document.getElementById('notif_email').checked,
            currency: document.getElementById('currency').value,
            language: document.getElementById('language').value
        };
        
        localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(preferences));
        
        AlertManager.show(this.alertDiv, 'success', 'Préférences enregistrées avec succès !');
    }
}

// ============================
// Gestionnaire d'Alertes
// ============================
class AlertManager {
    static show(alertElement, type, message, duration = 5000) {
        if (!alertElement) return;
        
        alertElement.className = `alert alert-${type}`;
        alertElement.innerHTML = `<i class="bi bi-${this.getIcon(type)}"></i> ${message}`;
        alertElement.classList.remove('d-none');
        
        if (duration > 0) {
            setTimeout(() => {
                alertElement.classList.add('d-none');
            }, duration);
        }
    }

    static getIcon(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-circle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// ============================
// Initialisation de l'Application
// ============================
let settingsNavigation;
let userProfileManager;
let accountsManager;
let preferencesManager;

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les gestionnaires
    settingsNavigation = new SettingsNavigation();
    userProfileManager = new UserProfileManager();
    accountsManager = new AccountsManager();
    preferencesManager = new PreferencesManager();
    
    console.log('PAYsible Settings - Initialized');
});
