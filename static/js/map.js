/* LocalRide — Leaflet.js + OpenStreetMap booking map (100% free, no API keys) */

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

function initBookingMap(config) {
  const DEFAULT_CENTER = [18.5204, 73.8567]; // Pune, India — sensible default
  const map = L.map(config.mapId).setView(DEFAULT_CENTER, 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);

  const teal = '#14E8B4', amber = '#FFB648';
  const pickupIcon = L.divIcon({ className: '', html: `<div style="width:18px;height:18px;border-radius:50%;background:${teal};border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>` });
  const dropIcon = L.divIcon({ className: '', html: `<div style="width:18px;height:18px;border-radius:50%;background:${amber};border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>` });

  let pickupMarker = null, dropMarker = null, routeLine = null, activeField = 'pickup';

  const pickupInput = document.getElementById(config.pickupInputId);
  const dropInput = document.getElementById(config.dropInputId);
  const pickupLatEl = document.getElementById(config.pickupLatId);
  const pickupLngEl = document.getElementById(config.pickupLngId);
  const dropLatEl = document.getElementById(config.dropLatId);
  const dropLngEl = document.getElementById(config.dropLngId);
  const setPickupBtn = document.getElementById('setPickupBtn');
  const setDropBtn = document.getElementById('setDropBtn');

  function setActive(field) {
    activeField = field;
    if (setPickupBtn) setPickupBtn.classList.toggle('btn-primary', field === 'pickup');
    if (setPickupBtn) setPickupBtn.classList.toggle('btn-outline', field !== 'pickup');
    if (setDropBtn) setDropBtn.classList.toggle('btn-primary', field === 'drop');
    if (setDropBtn) setDropBtn.classList.toggle('btn-outline', field !== 'drop');
  }
  setActive('pickup');
  if (setPickupBtn) setPickupBtn.addEventListener('click', () => setActive('pickup'));
  if (setDropBtn) setDropBtn.addEventListener('click', () => setActive('drop'));

  function placeMarker(lat, lng, field) {
    if (field === 'pickup') {
      if (pickupMarker) pickupMarker.setLatLng([lat, lng]);
      else pickupMarker = L.marker([lat, lng], { icon: pickupIcon, draggable: true }).addTo(map)
        .on('dragend', e => reverseGeocode(e.target.getLatLng(), 'pickup'));
      pickupLatEl.value = lat.toFixed(6);
      pickupLngEl.value = lng.toFixed(6);
    } else {
      if (dropMarker) dropMarker.setLatLng([lat, lng]);
      else dropMarker = L.marker([lat, lng], { icon: dropIcon, draggable: true }).addTo(map)
        .on('dragend', e => reverseGeocode(e.target.getLatLng(), 'drop'));
      dropLatEl.value = lat.toFixed(6);
      dropLngEl.value = lng.toFixed(6);
    }
    drawRoute();
    fetchFareEstimate();
  }

  function drawRoute() {
    if (pickupMarker && dropMarker) {
      const latlngs = [pickupMarker.getLatLng(), dropMarker.getLatLng()];
      if (routeLine) map.removeLayer(routeLine);
      routeLine = L.polyline(latlngs, { color: teal, weight: 4, dashArray: '8 10' }).addTo(map);
      map.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
    }
  }

  map.on('click', function (e) {
    placeMarker(e.latlng.lat, e.latlng.lng, activeField);
    reverseGeocode(e.latlng, activeField);
    if (activeField === 'pickup') setActive('drop');
  });

  /* --------- Reverse geocoding (Nominatim, free OSM service) --------- */
  function reverseGeocode(latlng, field) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latlng.lat}&lon=${latlng.lng}`)
      .then(r => r.json())
      .then(data => {
        const address = data.display_name || `${latlng.lat.toFixed(4)}, ${latlng.lng.toFixed(4)}`;
        if (field === 'pickup') pickupInput.value = address;
        else dropInput.value = address;
      })
      .catch(() => {});
  }

  /* --------- Forward geocoding search box with suggestions --------- */
  function attachSearch(inputEl, field) {
    let timer = null;
    const box = document.createElement('div');
    box.className = 'search-suggestions';
    box.style.cssText = 'position:relative;z-index:50;';
    inputEl.parentNode.appendChild(box);

    inputEl.addEventListener('input', function () {
      clearTimeout(timer);
      const q = inputEl.value.trim();
      box.innerHTML = '';
      if (q.length < 3) return;
      timer = setTimeout(() => {
        fetch(`https://nominatim.openstreetmap.org/search?format=json&limit=5&q=${encodeURIComponent(q)}`)
          .then(r => r.json())
          .then(results => {
            box.innerHTML = '';
            if (!results.length) return;
            const list = document.createElement('div');
            list.style.cssText = 'position:absolute;top:2px;left:0;right:0;background:var(--surface);border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow-md);max-height:220px;overflow:auto;';
            results.forEach(res => {
              const item = document.createElement('div');
              item.textContent = res.display_name;
              item.style.cssText = 'padding:10px 14px;font-size:13.5px;cursor:pointer;border-bottom:1px solid var(--line);';
              item.addEventListener('click', () => {
                inputEl.value = res.display_name;
                placeMarker(parseFloat(res.lat), parseFloat(res.lon), field);
                list.remove();
                if (field === 'pickup') setActive('drop');
              });
              list.appendChild(item);
            });
            box.appendChild(list);
          }).catch(() => {});
      }, 500);
    });
  }
  if (pickupInput) attachSearch(pickupInput, 'pickup');
  if (dropInput) attachSearch(dropInput, 'drop');

  /* --------- Use my current location for pickup --------- */
  const useLocationBtn = document.getElementById('useLocationBtn');
  if (useLocationBtn && navigator.geolocation) {
    useLocationBtn.addEventListener('click', function () {
      navigator.geolocation.getCurrentPosition(function (pos) {
        const { latitude, longitude } = pos.coords;
        map.setView([latitude, longitude], 15);
        placeMarker(latitude, longitude, 'pickup');
        reverseGeocode({ lat: latitude, lng: longitude }, 'pickup');
        setActive('drop');
      }, function () {
        alert('Could not get your location. Please search or click on the map.');
      });
    });
  }

  /* --------- Live fare estimate --------- */
  function fetchFareEstimate() {
    if (!pickupLatEl.value || !dropLatEl.value) return;
    fetch(config.fareApiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify({
        pickup_lat: pickupLatEl.value, pickup_lng: pickupLngEl.value,
        drop_lat: dropLatEl.value, drop_lng: dropLngEl.value,
        ride_type: getSelectedRideType(),
      }),
    })
      .then(r => r.json())
      .then(data => renderFareBox(data))
      .catch(() => {});
  }

  function getSelectedRideType() {
    const sel = document.querySelector('.vehicle-option.selected');
    return sel ? sel.dataset.type : 'mini';
  }

  function renderFareBox(data) {
    const distanceEl = document.getElementById('distanceValue');
    if (distanceEl) distanceEl.textContent = data.distance_km + ' km';
    Object.keys(data.estimates).forEach(function (type) {
      const est = data.estimates[type];
      const fareEl = document.getElementById('fare-' + type);
      const etaEl = document.getElementById('eta-' + type);
      if (fareEl) fareEl.textContent = '₹' + est.fare;
      if (etaEl) etaEl.textContent = Math.round(est.duration) + ' min';
    });
    const selectedType = getSelectedRideType();
    const totalEl = document.getElementById('totalFare');
    if (totalEl && data.estimates[selectedType]) totalEl.textContent = '₹' + data.estimates[selectedType].fare;
    document.getElementById('bookRideBtn')?.removeAttribute('disabled');
  }

  document.querySelectorAll('.vehicle-option').forEach(function (opt) {
    opt.addEventListener('click', function () {
      document.querySelectorAll('.vehicle-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      document.getElementById('rideTypeInput').value = opt.dataset.type;
      fetchFareEstimate();
    });
  });

  return map;
}

/* Small static route SVG animation used on ride-detail / tracking pages */
function drawStaticRoute(mapId, pickup, drop) {
  const map = L.map(mapId).setView(pickup, 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map);
  const teal = '#14E8B4', amber = '#FFB648';
  L.marker(pickup, { icon: L.divIcon({ className: '', html: `<div style="width:16px;height:16px;border-radius:50%;background:${teal};border:3px solid #fff"></div>` }) }).addTo(map);
  L.marker(drop, { icon: L.divIcon({ className: '', html: `<div style="width:16px;height:16px;border-radius:50%;background:${amber};border:3px solid #fff"></div>` }) }).addTo(map);
  const line = L.polyline([pickup, drop], { color: teal, weight: 4, dashArray: '8 10' }).addTo(map);
  map.fitBounds(line.getBounds(), { padding: [40, 40] });
}
