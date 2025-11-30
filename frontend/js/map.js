// Inicialización del mapa Leaflet
const map = L.map('map').setView([22.2355, -101.2356], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

L.marker([22.2355, -101.2356])
    .addTo(map)
    .bindPopup('Sensor Location')
    .openPopup();
