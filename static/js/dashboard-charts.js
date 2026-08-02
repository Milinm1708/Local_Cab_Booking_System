/* LocalRide — Chart.js dashboard visualisations */

function renderRidesByStatusChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: ['#FFB648', '#2C5FD6', '#8A6CFF', '#14E8B4', '#FF5D6C', '#B0B8CC'],
        borderWidth: 0,
      }],
    },
    options: {
      plugins: { legend: { position: 'bottom', labels: { color: getComputedStyle(document.body).color, padding: 16 } } },
      cutout: '65%',
    },
  });
}

function renderRevenueTrendChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Revenue (Rs)',
        data: values,
        borderColor: '#14E8B4',
        backgroundColor: 'rgba(20,232,180,.15)',
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#14E8B4',
      }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: getComputedStyle(document.body).color } },
        y: { grid: { color: 'rgba(128,128,128,.15)' }, ticks: { color: getComputedStyle(document.body).color } },
      },
    },
  });
}

function renderRideTypeChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Rides',
        data: values,
        backgroundColor: '#2C5FD6',
        borderRadius: 8,
        maxBarThickness: 46,
      }],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: getComputedStyle(document.body).color } },
        y: { grid: { color: 'rgba(128,128,128,.15)' }, ticks: { color: getComputedStyle(document.body).color } },
      },
    },
  });
}
