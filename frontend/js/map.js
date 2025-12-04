const map = L.map('map').setView([20.61342647141931, -100.40629074921955], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

L.marker([20.61342647141931, -100.40629074921955])
    .addTo(map)
    .bindPopup('TEC de Monterrey - Campus Querétaro')
    .openPopup();