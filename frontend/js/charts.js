let waterChart, tempHumidityChart;

function updateCharts(data) {
    const labels = data.map(d => new Date(d.registration_date).toLocaleTimeString()).reverse();
    const waterLevels = data.map(d => d.water_level_cm).reverse();
    const temperatures = data.map(d => d.temperature_c).reverse();
    const humidities = data.map(d => d.humidity_percentage).reverse();

    if (waterChart) waterChart.destroy();
    waterChart = new Chart(document.getElementById('waterChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Water Level (cm)',
                data: waterLevels,
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231,76,60,0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    if (tempHumidityChart) tempHumidityChart.destroy();
    tempHumidityChart = new Chart(document.getElementById('tempHumidityChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52,152,219,0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                },
                {
                    label: 'Humidity (%)',
                    data: humidities,
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243,156,18,0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
