// virement.js - Gestion des virements

document.addEventListener('DOMContentLoaded', function() {
    // Gestion des clics sur les cartes
    const cardInterne = document.getElementById('card-interne');
    const cardBeneficiaire = document.getElementById('card-beneficiaire');
    
    if (cardInterne) {
        cardInterne.addEventListener('click', () => showTab('interne'));
    }
    
    if (cardBeneficiaire) {
        cardBeneficiaire.addEventListener('click', () => showTab('beneficiaire'));
    }
    
    // Gestion de la soumission du formulaire virement interne
    const formVirementInterne = document.getElementById('form-virement-interne');
    if (formVirementInterne) {
        formVirementInterne.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleVirementInterne(e.target);
        });
    }
    
    // Gestion de la soumission du formulaire virement bénéficiaire
    const formVirementBenef = document.getElementById('form-virement-beneficiaire');
    if (formVirementBenef) {
        formVirementBenef.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleVirementBeneficiaire(e.target);
        });
    }
});

/**
 * Affiche le formulaire correspondant au type de virement sélectionné
 * @param {string} type - Type de virement ('interne' ou 'beneficiaire')
 */
function showTab(type) {
    // Cacher tous les formulaires
    const formInterne = document.getElementById('form-interne');
    const formBeneficiaire = document.getElementById('form-beneficiaire');
    
    if (formInterne) formInterne.style.display = 'none';
    if (formBeneficiaire) formBeneficiaire.style.display = 'none';
    
    // Désélectionner toutes les cartes
    document.querySelectorAll('.virement-type-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Afficher le bon formulaire et sélectionner la carte
    if (type === 'interne' && formInterne) {
        formInterne.style.display = 'block';
        document.getElementById('card-interne')?.classList.add('selected');
        setTimeout(() => formInterne.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    } else if (type === 'beneficiaire' && formBeneficiaire) {
        formBeneficiaire.style.display = 'block';
        document.getElementById('card-beneficiaire')?.classList.add('selected');
        setTimeout(() => formBeneficiaire.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }
}

/**
 * Réinitialise l'affichage en masquant tous les formulaires
 */
function resetForm() {
    const formInterne = document.getElementById('form-interne');
    const formBeneficiaire = document.getElementById('form-beneficiaire');
    
    if (formInterne) formInterne.style.display = 'none';
    if (formBeneficiaire) formBeneficiaire.style.display = 'none';
    
    document.querySelectorAll('.virement-type-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Gère la soumission du formulaire de virement interne via API
 * @param {HTMLFormElement} form - Le formulaire soumis
 */
async function handleVirementInterne(form) {
    const formData = new FormData(form);
    const data = {
        compte_debit: parseInt(formData.get('compte_debit')),
        compte_credit: parseInt(formData.get('compte_credit')),
        montant: parseFloat(formData.get('montant')),
        description: formData.get('description') || ''
    };
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Désactiver le bouton et afficher le loader
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Traitement...';
        
        const response = await fetch('/api/virements/interne', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Succès
            showAlert('success', result.message, form);
            form.reset();
            
            // Redirection après 2 secondes
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        } else {
            // Erreur du serveur
            showAlert('danger', result.detail || 'Une erreur est survenue', form);
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('danger', 'Erreur de connexion au serveur', form);
    } finally {
        // Réactiver le bouton
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

/**
 * Gère la soumission du formulaire de virement vers bénéficiaire via API
 * @param {HTMLFormElement} form - Le formulaire soumis
 */
async function handleVirementBeneficiaire(form) {
    const formData = new FormData(form);
    const data = {
        compte_debit: parseInt(formData.get('compte_debit')),
        beneficiaire_id: parseInt(formData.get('beneficiaire_id')),
        montant: parseFloat(formData.get('montant')),
        description: formData.get('description') || ''
    };
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Désactiver le bouton et afficher le loader
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Traitement...';
        
        const response = await fetch('/api/virements/beneficiaire', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Succès
            showAlert('success', result.message, form);
            form.reset();
            
            // Redirection après 2 secondes
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 2000);
        } else {
            // Erreur du serveur
            showAlert('danger', result.detail || 'Une erreur est survenue', form);
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('danger', 'Erreur de connexion au serveur', form);
    } finally {
        // Réactiver le bouton
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

/**
 * Affiche une alerte Bootstrap
 * @param {string} type - Type d'alerte (success, danger, warning, info)
 * @param {string} message - Message à afficher
 * @param {HTMLFormElement} form - Le formulaire où insérer l'alerte
 */
function showAlert(type, message, form) {
    // Supprimer les anciennes alertes
    const oldAlerts = form.parentElement.querySelectorAll('.alert');
    oldAlerts.forEach(alert => alert.remove());
    
    // Créer la nouvelle alerte
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insérer l'alerte avant le formulaire
    form.parentElement.insertBefore(alertDiv, form);
    
    // Faire défiler vers l'alerte
    alertDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto-dismiss après 5 secondes
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
