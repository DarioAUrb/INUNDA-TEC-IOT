let waterChart;

function updateCharts(data) {
    const labels = data.map(d => new Date(d.registration_date).toLocaleTimeString()).reverse();
    const waterLevels = data.map(d => d.water_level_cm).reverse();

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
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: '#e74c3c'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#ecf0f1'
                    }
                }
            },
            scales: {
                y: {
                    ticks: { color: '#95a5a6' },
                    grid: { color: '#3a4451' }
                },
                x: {
                    ticks: { color: '#95a5a6' },
                    grid: { color: '#3a4451' }
                }
            }
        }
    });
}