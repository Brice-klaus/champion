document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('magasin-map');
  if (!container) return;

  mapboxgl.accessToken = container.dataset.token;

  const lat = parseFloat(container.dataset.lat);
  const lng = parseFloat(container.dataset.lng);

  const latInput = document.getElementById('id_latitude');
  const lngInput = document.getElementById('id_longitude');

  const map = new mapboxgl.Map({
    container: 'magasin-map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [lng, lat],
    zoom: 13,
  });

  map.on('load', () => map.resize());

// Sécurité supplémentaire si le layout admin se stabilise après le premier rendu
window.addEventListener('load', () => map.resize());

  map.addControl(new mapboxgl.NavigationControl());

  const marker = new mapboxgl.Marker({ draggable: true, color: '#E2231A' })
    .setLngLat([lng, lat])
    .addTo(map);

  function syncInputs(lngLat) {
    latInput.value = lngLat.lat.toFixed(6);
    lngInput.value = lngLat.lng.toFixed(6);
  }

  marker.on('dragend', () => syncInputs(marker.getLngLat()));

  // Clic sur la carte : déplace le marqueur à cet endroit
  map.on('click', (e) => {
    marker.setLngLat(e.lngLat);
    syncInputs(e.lngLat);
  });

  // Recherche d'adresse simple via l'API Geocoding Mapbox
  const searchBox = document.createElement('input');
  searchBox.type = 'text';
  searchBox.placeholder = 'Rechercher une adresse à Lomé...';
  searchBox.className = 'magasin-map-search';
  container.parentElement.insertBefore(searchBox, container);

  let debounceTimer;
  searchBox.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const query = searchBox.value.trim();
    if (query.length < 3) return;

    debounceTimer = setTimeout(async () => {
      const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${mapboxgl.accessToken}&country=TG&limit=1`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.features && data.features.length) {
        const [foundLng, foundLat] = data.features[0].center;
        map.flyTo({ center: [foundLng, foundLat], zoom: 15 });
        marker.setLngLat([foundLng, foundLat]);
        syncInputs({ lat: foundLat, lng: foundLng });
      }
    }, 900);
  });
});