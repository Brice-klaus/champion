document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('magasins-map');
  if (!el) return;

  let magasins = [];
  try {
    magasins = JSON.parse(el.dataset.magasins);
  } catch (e) {
    magasins = [];
  }

  const valides = magasins.filter(m => m.lat && m.lng);
  if (!valides.length) {
    el.innerHTML = '';
    return;
  }

  mapboxgl.accessToken = el.dataset.token;

  const map = new mapboxgl.Map({
    container: 'magasins-map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [valides[0].lng, valides[0].lat],
    zoom: 7,
  });

  map.on('load', () => map.resize());
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');

  const bounds = new mapboxgl.LngLatBounds();

  valides.forEach((m) => {
    const marker = new mapboxgl.Marker({ color: '#E2231A' })
      .setLngLat([m.lng, m.lat])
      .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(`<strong>${m.nom}</strong><br>${m.adresse}`))
      .addTo(map);

    marker.getElement().style.cursor = 'pointer';
    marker.getElement().addEventListener('click', () => {
      const card = document.getElementById(`magasin-card-${m.id}`);
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.classList.add('ring-2', 'ring-champion-500');
        setTimeout(() => card.classList.remove('ring-2', 'ring-champion-500'), 1800);
      }
    });

    bounds.extend([m.lng, m.lat]);
  });

  if (valides.length > 1) {
    map.fitBounds(bounds, { padding: 60, maxZoom: 14 });
  }
});