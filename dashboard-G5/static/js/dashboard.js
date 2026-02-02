// ============================================
// SDID Energy Monitor - Dashboard JavaScript
// Gestion des graphiques Plotly et mise à jour temps réel
// ============================================

// Configuration globale
const UPDATE_INTERVAL = 3000; // Mise à jour toutes les 3 secondes
let updateTimer;

// ============================================
// INITIALISATION AU CHARGEMENT DE LA PAGE
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard SDID initialisé');

    // Initialiser tous les graphiques
    initCharts();

    // Première récupération des données
    fetchData();
    fetchStats();
    fetchAnomalies();

    // Lancer les mises à jour automatiques
    startAutoUpdate();
});

// ============================================
// INITIALISATION DES GRAPHIQUES PLOTLY
// ============================================

function initCharts() {
    // Configuration commune pour tous les graphiques
    const commonLayout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(26, 31, 53, 0.5)',
        font: {
            family: 'Rajdhani, sans-serif',
            color: '#e8edf5'
        },
        margin: { t: 40, r: 30, b: 50, l: 60 },
        xaxis: {
            gridcolor: '#2a3150',
            showgrid: true
        },
        yaxis: {
            gridcolor: '#2a3150',
            showgrid: true
        }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    // Graphique 1 : Puissance Active
    const powerData = [{
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Puissance Active',
        line: {
            color: '#00d9ff',
            width: 3,
            shape: 'spline'
        },
        marker: {
            color: '#00d9ff',
            size: 6,
            line: {
                color: '#00ff88',
                width: 1
            }
        }
    }];

    const powerLayout = {
        ...commonLayout,
        title: {
            text: 'Puissance Active Globale (kW)',
            font: { size: 16, color: '#00d9ff' }
        },
        yaxis: {
            ...commonLayout.yaxis,
            title: 'Puissance (kW)'
        }
    };

    Plotly.newPlot('powerChart', powerData, powerLayout, config);

    // Graphique 2 : Tension
    const voltageData = [{
        x: [],
        y: [],
        type: 'scatter',
        mode: 'lines',
        name: 'Tension',
        fill: 'tozeroy',
        line: {
            color: '#00ff88',
            width: 2
        },
        fillcolor: 'rgba(0, 255, 136, 0.2)'
    }];

    const voltageLayout = {
        ...commonLayout,
        title: {
            text: 'Tension (V)',
            font: { size: 14, color: '#00ff88' }
        },
        yaxis: {
            ...commonLayout.yaxis,
            title: 'Volts'
        }
    };

    Plotly.newPlot('voltageChart', voltageData, voltageLayout, config);

    // Graphique 3 : Intensité
    const intensityData = [{
        x: [],
        y: [],
        type: 'bar',
        name: 'Intensité',
        marker: {
            color: '#ffaa00',
            line: {
                color: '#ff8800',
                width: 1
            }
        }
    }];

    const intensityLayout = {
        ...commonLayout,
        title: {
            text: 'Intensité Globale (A)',
            font: { size: 14, color: '#ffaa00' }
        },
        yaxis: {
            ...commonLayout.yaxis,
            title: 'Ampères'
        }
    };

    Plotly.newPlot('intensityChart', intensityData, intensityLayout, config);

    // Graphique 4 : Sous-compteurs (Pie Chart)
    const submeteringData = [{
        labels: ['Sous-compteur 1', 'Sous-compteur 2', 'Sous-compteur 3'],
        values: [0, 0, 0],
        type: 'pie',
        marker: {
            colors: ['#00d9ff', '#00ff88', '#bb86fc'],
            line: {
                color: '#1a1f35',
                width: 2
            }
        },
        textfont: {
            color: '#ffffff',
            size: 14
        }
    }];

    const submeteringLayout = {
        ...commonLayout,
        title: {
            text: 'Répartition des Sous-compteurs',
            font: { size: 14, color: '#bb86fc' }
        },
        showlegend: true,
        legend: {
            font: { color: '#e8edf5' }
        }
    };

    Plotly.newPlot('submeteringChart', submeteringData, submeteringLayout, config);
}

// ============================================
// RÉCUPÉRATION DES DONNÉES VIA API
// ============================================

async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            updateCharts(result.data);
            updateLastUpdateTime();
        } else {
            console.warn('⚠️ Aucune donnée disponible');
        }
    } catch (error) {
        console.error('❌ Erreur lors de la récupération des données:', error);
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const result = await response.json();

        if (result.success) {
            updateKPIs(result.stats);
        }
    } catch (error) {
        console.error('❌ Erreur lors de la récupération des statistiques:', error);
    }
}

async function fetchAnomalies() {
    try {
        const response = await fetch('/api/anomalies');
        const result = await response.json();

        if (result.success) {
            updateAnomaliesTable(result.anomalies);
            checkForNewAnomalies(result.anomalies);
        }
    } catch (error) {
        console.error('❌ Erreur lors de la récupération des anomalies:', error);
    }
}

// ============================================
// MISE À JOUR DES GRAPHIQUES
// ============================================

function updateCharts(data) {
    // Inverser l'ordre pour afficher du plus ancien au plus récent
    data = data.reverse();

    // Extraire les données
    const timestamps = data.map(d => new Date(d.timestamp));
    const powers = data.map(d => d.global_active_power || 0);
    const voltages = data.map(d => d.voltage || 0);
    const intensities = data.map(d => d.global_intensity || 0);

    // Calculer les moyennes des sous-compteurs
    const sub1_avg = data.reduce((sum, d) => sum + (d.sub_metering_1 || 0), 0) / data.length;
    const sub2_avg = data.reduce((sum, d) => sum + (d.sub_metering_2 || 0), 0) / data.length;
    const sub3_avg = data.reduce((sum, d) => sum + (d.sub_metering_3 || 0), 0) / data.length;

    // Marquer les anomalies en rouge
    const colors = data.map(d => d.is_anomaly ? '#ff3366' : '#00d9ff');

    // Mise à jour Graphique Puissance
    Plotly.update('powerChart', {
        x: [timestamps],
        y: [powers],
        'marker.color': [colors]
    }, {}, [0]);

    // Mise à jour Graphique Tension
    Plotly.update('voltageChart', {
        x: [timestamps],
        y: [voltages]
    }, {}, [0]);

    // Mise à jour Graphique Intensité (limiter à 20 dernières valeurs pour lisibilité)
    const recentTimestamps = timestamps.slice(-20);
    const recentIntensities = intensities.slice(-20);

    Plotly.update('intensityChart', {
        x: [recentTimestamps],
        y: [recentIntensities]
    }, {}, [0]);

    // Mise à jour Graphique Sous-compteurs
    Plotly.update('submeteringChart', {
        values: [[sub1_avg, sub2_avg, sub3_avg]]
    }, {}, [0]);
}

// ============================================
// MISE À JOUR DES KPIs
// ============================================

function updateKPIs(stats) {
    document.getElementById('totalRecords').textContent = stats.total_records.toLocaleString();
    document.getElementById('totalAnomalies').textContent = stats.total_anomalies.toLocaleString();
    document.getElementById('avgPower').textContent = stats.avg_power.toFixed(2);
    document.getElementById('avgVoltage').textContent = stats.avg_voltage.toFixed(1);
}

// ============================================
// MISE À JOUR DU TABLEAU DES ANOMALIES
// ============================================

function updateAnomaliesTable(anomalies) {
    const tbody = document.getElementById('anomaliesTable');
    const anomalyCountBadge = document.getElementById('anomalyCount');

    anomalyCountBadge.textContent = `${anomalies.length} alerte${anomalies.length > 1 ? 's' : ''}`;

    if (anomalies.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    Aucune anomalie détectée pour le moment...
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = anomalies.map(anomaly => `
        <tr class="table-row-anomaly">
            <td>${new Date(anomaly.timestamp).toLocaleString('fr-FR')}</td>
            <td><strong>${(anomaly.power || 0).toFixed(3)}</strong> kW</td>
            <td><strong>${(anomaly.voltage || 0).toFixed(1)}</strong> V</td>
            <td><span class="badge bg-warning">${(anomaly.score || 0).toFixed(3)}</span></td>
            <td><span class="anomaly-badge badge-critical">CRITIQUE</span></td>
        </tr>
    `).join('');
}

// ============================================
// SYSTÈME D'ALERTES
// ============================================

let lastAnomalyCount = 0;

function checkForNewAnomalies(anomalies) {
    if (anomalies.length > lastAnomalyCount && lastAnomalyCount > 0) {
        // Nouvelle anomalie détectée !
        showAlert(anomalies[0]);
    }
    lastAnomalyCount = anomalies.length;
}

function showAlert(anomaly) {
    const banner = document.getElementById('alertBanner');
    const message = document.getElementById('alertMessage');

    message.textContent = `Anomalie détectée à ${new Date(anomaly.timestamp).toLocaleTimeString('fr-FR')} - Puissance: ${(anomaly.power || 0).toFixed(2)} kW`;

    banner.style.display = 'block';

    // Jouer un son d'alerte (optionnel)
    playAlertSound();

    // Auto-fermeture après 10 secondes
    setTimeout(() => {
        dismissAlert();
    }, 10000);
}

function dismissAlert() {
    const banner = document.getElementById('alertBanner');
    banner.style.display = 'none';
}

function playAlertSound() {
    // Créer un bip sonore simple
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
        console.log('Son d\'alerte non disponible');
    }
}

// ============================================
// MISE À JOUR AUTOMATIQUE
// ============================================

function startAutoUpdate() {
    updateTimer = setInterval(() => {
        fetchData();
        fetchStats();
        fetchAnomalies();
    }, UPDATE_INTERVAL);

    console.log(`✅ Mise à jour automatique activée (intervalle: ${UPDATE_INTERVAL}ms)`);
}

function stopAutoUpdate() {
    if (updateTimer) {
        clearInterval(updateTimer);
        console.log('⏸️ Mise à jour automatique arrêtée');
    }
}

// ============================================
// UTILITAIRES
// ============================================

function updateLastUpdateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('fr-FR');
    document.getElementById('lastUpdate').textContent = timeString;
}

// Arrêter les mises à jour si l'utilisateur quitte la page
window.addEventListener('beforeunload', () => {
    stopAutoUpdate();
});
