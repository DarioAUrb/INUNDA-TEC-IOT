const WATER_THRESHOLD_WARNING = 5;
const WATER_THRESHOLD_DANGER = 9;

// Obtener datos de sensores
async function fetchSensorData() {
    try {
        const response = await fetch('http://localhost:8000/sensors?limit=50');
        const data = await response.json();

        if (data.status === 'success' && data.data.length > 0) {
            const lastRecord = data.data[0];

            document.getElementById('waterLevel').textContent = (lastRecord.water_level_cm || 0).toFixed(2);
            document.getElementById('temperature').textContent = (lastRecord.temperature_c || 0).toFixed(1);
            document.getElementById('humidity').textContent = (lastRecord.humidity_percentage || 0).toFixed(0);

            updateCharts(data.data);
            checkWaterLevelAlerts(lastRecord.water_level_cm);
        }
    } catch (error) {
        console.error("Error fetching sensor data:", error);
    }
}

// Obtener estadísticas
async function fetchStatistics() {
    try {
        const response = await fetch('http://localhost:8000/sensors/statistics');
        const data = await response.json();

        if (data.status === 'success') {
            const water = data.water_level_cm;
            const temp = data.temperature_c;
            const humidity = data.humidity_percentage;

            document.getElementById('statWaterMin').textContent = water.min || '--';
            document.getElementById('statWaterMax').textContent = water.max || '--';
            document.getElementById('statWaterAvg').textContent = water.average || '--';

            document.getElementById('statTempMin').textContent = temp.min || '--';
            document.getElementById('statTempMax').textContent = temp.max || '--';
            document.getElementById('statTempAvg').textContent = temp.average || '--';

            document.getElementById('statHumMin').textContent = humidity.min || '--';
            document.getElementById('statHumMax').textContent = humidity.max || '--';
            document.getElementById('statHumAvg').textContent = humidity.average || '--';
        }
    } catch (error) {
        console.error("Error fetching statistics:", error);
    }
}

// Verificar alertas de nivel de agua
function checkWaterLevelAlerts(waterLevel) {
    const alertsBox = document.getElementById('alertsBox');
    alertsBox.innerHTML = '';

    if (waterLevel >= WATER_THRESHOLD_DANGER) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.innerHTML = `<i class="fas fa-exclamation-circle"></i> PELIGRO: Nivel crítico (${waterLevel.toFixed(2)} cm)`;
        alertsBox.appendChild(alert);
    } else if (waterLevel >= WATER_THRESHOLD_WARNING) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-warning';
        alert.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Advertencia: Nivel elevado (${waterLevel.toFixed(2)} cm)`;
        alertsBox.appendChild(alert);
    } else {
        const noAlert = document.createElement('div');
        noAlert.className = 'no-alerts';
        noAlert.textContent = 'Sin alertas';
        alertsBox.appendChild(noAlert);
    }
}

// Cargar datos al iniciar
window.addEventListener("load", () => {
    fetchSensorData();
    fetchStatistics();
});

// Actualizar cada 5 segundos
setInterval(() => {
    fetchSensorData();
    fetchStatistics();
}, 5000);