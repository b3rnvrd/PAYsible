// dashboard.js - Gestion des graphiques du tableau de bord

// --- Configuration commune pour tous les graphiques ---
const commonOptions = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
        x: { grid: { display: false } },
        y: { grid: { borderDash: [5, 5] } }
    },
    elements: {
        line: { tension: 0.4 },
        point: { radius: 3, hoverRadius: 6 }
    }
};

// Palette de couleurs pour le graphique en camembert
const colors = [
    '#1D3D6A', '#38A5E4', '#F4C448', '#2474C6', '#6610f2', 
    '#20c997', '#dc3545', '#fd7e14', '#e83e8c', '#6f42c1',
    '#17a2b8', '#ffc107', '#28a745', '#343a40', '#6c757d'
];

/**
 * Initialise les graphiques linéaires pour chaque compte
 * @param {Array} accountsData - Données des comptes avec labels et data
 */
function initAccountCharts(accountsData) {
    accountsData.forEach(account => {
        const canvas = document.getElementById(`chart-account-${account.id}`);
        if (!canvas) return;

        new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: account.labels,
                datasets: [{
                    label: 'Solde (€)',
                    data: account.data,
                    borderColor: '#38A5E4',
                    backgroundColor: 'rgba(56, 165, 228, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    pointBackgroundColor: '#1D3D6A'
                }]
            },
            options: commonOptions
        });
    });
}

/**
 * Initialise le graphique en camembert des dépenses
 * @param {Array} labels - Libellés des catégories
 * @param {Array} data - Montants par catégorie
 */
function initExpensesChart(labels, data) {
    const ctxPie = document.getElementById('expensesChart');
    if (!ctxPie) return;

    // Création du graphique
    new Chart(ctxPie.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) { label += ': '; }
                            let value = context.raw;
                            label += value.toFixed(2) + ' €';
                            return label;
                        }
                    }
                }
            },
            cutout: '70%',
            layout: { padding: 0 }
        }
    });

    // Génération de la légende HTML personnalisée
    generateLegend(labels);
}

/**
 * Génère une légende HTML personnalisée pour le graphique
 * @param {Array} labels - Libellés des catégories
 */
function generateLegend(labels) {
    const legendContainer = document.getElementById('js-legend');
    if (!legendContainer) return;

    legendContainer.innerHTML = '';

    labels.forEach((label, index) => {
        const color = colors[index % colors.length];
        
        const item = document.createElement('div');
        item.className = 'd-flex align-items-center mb-1 me-2';
        item.style.fontSize = '0.85rem';
        
        const box = document.createElement('span');
        box.style.display = 'inline-block';
        box.style.width = '12px';
        box.style.height = '12px';
        box.style.backgroundColor = color;
        box.style.borderRadius = '3px';
        box.style.marginRight = '6px';

        const text = document.createElement('span');
        text.innerText = label;
        text.className = 'text-muted';

        item.appendChild(box);
        item.appendChild(text);
        legendContainer.appendChild(item);
    });
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Les données sont injectées par le template dans des attributs data-*
    const accountsDataElement = document.getElementById('accounts-data');
    const pieDataElement = document.getElementById('pie-data');

    if (accountsDataElement) {
        const accountsData = JSON.parse(accountsDataElement.dataset.accounts || '[]');
        initAccountCharts(accountsData);
    }

    if (pieDataElement) {
        const pieLabels = JSON.parse(pieDataElement.dataset.labels || '[]');
        const pieData = JSON.parse(pieDataElement.dataset.data || '[]');
        initExpensesChart(pieLabels, pieData);
    }
});
