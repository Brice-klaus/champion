document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('magasin-detail-map');
  if (!el) return;

  mapboxgl.accessToken = el.dataset.token;

  // Normalise une éventuelle virgule décimale avant parseFloat
  const lat = parseFloat(String(el.dataset.lat).replace(',', '.'));
  const lng = parseFloat(String(el.dataset.lng).replace(',', '.'));

  if (Number.isNaN(lat) || Number.isNaN(lng)) {
    console.error('[magasin-detail-map] Coordonnées invalides :', el.dataset.lat, el.dataset.lng);
    el.innerHTML = '<p style="padding:16px;color:#c11912;">Localisation indisponible.</p>';
    return;
  }

  const map = new mapboxgl.Map({
    container: 'magasin-detail-map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [lng, lat],
    zoom: 13,
    scrollZoom: false,
  });

  map.on('load', () => map.resize());
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');

  new mapboxgl.Marker({ color: '#E2231A' })
    .setLngLat([lng, lat])
    .setPopup(
      new mapboxgl.Popup({ offset: 25 }).setHTML(
        `<strong>${el.dataset.nom}</strong><br>${el.dataset.adresse}`
      )
    )
    .addTo(map);
});