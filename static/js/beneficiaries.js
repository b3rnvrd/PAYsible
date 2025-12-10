// beneficiaries.js - Gestion des bénéficiaires via API

const API_URL = "/api/beneficiaries/";

/**
 * Affiche un message d'alerte à l'utilisateur
 * @param {string} message - Message à afficher
 * @param {string} type - Type d'alerte (danger, success, warning, info)
 */
function showAlert(message, type = "danger") {
    const container = document.getElementById('alert-container');
    if (!container) return;

    container.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}-fill me-2"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    container.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Charge et affiche la liste des bénéficiaires
 */
async function loadBeneficiaries() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            showAlert("Erreur lors du chargement des bénéficiaires", "warning");
            return;
        }

        const data = await response.json();
        const listElement = document.getElementById('beneficiaryList');
        if (!listElement) return;

        listElement.innerHTML = "";

        if (data.length === 0) {
            listElement.innerHTML = `
                <tr>
                    <td colspan="3" class="text-center text-muted py-4">
                        <i class="bi bi-inbox"></i> Aucun bénéficiaire enregistré
                    </td>
                </tr>
            `;
            return;
        }

        data.forEach(beneficiary => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold text-dark">${escapeHtml(beneficiary.name)}</td>
                <td class="font-monospace text-muted small">${escapeHtml(beneficiary.iban)}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="prefillUpdate(${beneficiary.id}, '${escapeHtml(beneficiary.name)}', '${escapeHtml(beneficiary.iban)}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteBeneficiary(${beneficiary.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            listElement.appendChild(tr);
        });
    } catch (error) {
        console.error("Erreur lors du chargement des bénéficiaires:", error);
        showAlert("Erreur de connexion au serveur", "danger");
    }
}

/**
 * Ajoute un nouveau bénéficiaire
 */
async function addBeneficiary() {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) alertContainer.innerHTML = "";

    const name = document.getElementById('newName')?.value.trim();
    const iban = document.getElementById('newIban')?.value.trim();
    
    if (!name || !iban) {
        showAlert("Veuillez remplir tous les champs (Nom et IBAN).", "warning");
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, iban })
        });

        if (response.ok) {
            document.getElementById('newName').value = "";
            document.getElementById('newIban').value = "";
            await loadBeneficiaries();
            showAlert("Bénéficiaire ajouté avec succès !", "success");
        } else {
            const errorData = await response.json();
            let message = "Impossible d'ajouter le bénéficiaire.";

            if (response.status === 422 && errorData.detail) {
                message = errorData.detail[0]?.msg?.replace('Value error, ', '') || message;
            } else if (errorData.detail) {
                message = errorData.detail;
            }
            showAlert(message, "danger");
        }
    } catch (error) {
        console.error("Erreur lors de l'ajout:", error);
        showAlert("Erreur de connexion au serveur", "danger");
    }
}

/**
 * Met à jour un bénéficiaire existant
 */
async function updateBeneficiary() {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) alertContainer.innerHTML = "";
    
    const id = document.getElementById('updateId')?.value;
    if (!id) {
        showAlert("Sélectionnez un bénéficiaire dans la liste d'abord", "warning");
        return;
    }
    
    const name = document.getElementById('updateName')?.value.trim();
    const iban = document.getElementById('updateIban')?.value.trim();

    if (!name && !iban) {
        showAlert("Veuillez modifier au moins un champ", "warning");
        return;
    }

    try {
        const response = await fetch(`${API_URL}${id}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, iban })
        });
        
        if (response.ok) {
            await loadBeneficiaries();
            document.getElementById('updateId').value = "";
            document.getElementById('updateName').value = "";
            document.getElementById('updateIban').value = "";
            showAlert("Modification enregistrée.", "success");
        } else {
            const errorData = await response.json();
            let message = errorData.detail || "Erreur lors de la modification";
            
            if (response.status === 422 && errorData.detail[0]) {
                message = errorData.detail[0].msg?.replace('Value error, ', '') || message;
            }
            showAlert(message, "danger");
        }
    } catch (error) {
        console.error("Erreur lors de la modification:", error);
        showAlert("Erreur de connexion au serveur", "danger");
    }
}

/**
 * Supprime un bénéficiaire
 * @param {number} id - ID du bénéficiaire à supprimer
 */
async function deleteBeneficiary(id) {
    if (!confirm("Êtes-vous sûr de vouloir supprimer ce bénéficiaire ?")) return;

    try {
        const response = await fetch(`${API_URL}${id}/`, { 
            method: 'DELETE' 
        });

        if (response.ok) {
            await loadBeneficiaries();
            showAlert("Bénéficiaire supprimé avec succès", "success");
        } else {
            showAlert("Erreur lors de la suppression", "danger");
        }
    } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        showAlert("Erreur de connexion au serveur", "danger");
    }
}

/**
 * Pré-remplit le formulaire de modification
 * @param {number} id - ID du bénéficiaire
 * @param {string} name - Nom du bénéficiaire
 * @param {string} iban - IBAN du bénéficiaire
 */
function prefillUpdate(id, name, iban) {
    document.getElementById('updateId').value = id;
    document.getElementById('updateName').value = name;
    document.getElementById('updateIban').value = iban;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) alertContainer.innerHTML = "";
}

/**
 * Échappe les caractères HTML pour éviter les injections XSS
 * @param {string} text - Texte à échapper
 * @returns {string} Texte échappé
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", loadBeneficiaries);
