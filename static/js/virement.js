// virement.js - Gestion des virements

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
 * Valide que les comptes de débit et crédit sont différents
 * @param {HTMLSelectElement} changedSelect - Le select qui a changé
 * @param {HTMLSelectElement} otherSelect - L'autre select à vérifier
 */
function validateDifferentAccounts(changedSelect, otherSelect) {
    if (changedSelect.value && otherSelect.value === changedSelect.value) {
        alert('Vous ne pouvez pas sélectionner le même compte pour le débit et le crédit.');
        changedSelect.value = '';
    }
}

/**
 * Initialise les événements de la page
 */
function initVirementEvents() {
    // Écouteurs pour les cartes de sélection de type
    const cardInterne = document.getElementById('card-interne');
    const cardBeneficiaire = document.getElementById('card-beneficiaire');
    
    if (cardInterne) {
        cardInterne.addEventListener('click', () => showTab('interne'));
    }
    
    if (cardBeneficiaire) {
        cardBeneficiaire.addEventListener('click', () => showTab('beneficiaire'));
    }

    // Validation pour les virements internes
    const compteDebit = document.getElementById('compte_debit');
    const compteCredit = document.getElementById('compte_credit');
    
    if (compteDebit && compteCredit) {
        compteDebit.addEventListener('change', function() {
            validateDifferentAccounts(this, compteCredit);
        });
        
        compteCredit.addEventListener('change', function() {
            validateDifferentAccounts(this, compteDebit);
        });
    }
}

/**
 * Détecte et affiche le bon formulaire si une erreur/succès est présent
 */
function detectFormWithAlert() {
    const errorInterne = document.querySelector('#form-interne .alert');
    if (errorInterne) {
        showTab('interne');
        return;
    }

    const errorBenef = document.querySelector('#form-beneficiaire .alert');
    if (errorBenef) {
        showTab('beneficiaire');
    }
}

// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", function() {
    initVirementEvents();
    detectFormWithAlert();
});
