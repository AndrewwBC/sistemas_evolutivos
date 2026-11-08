/**
 * UFPel Chart.js theme + auto-initializer.
 *
 * Usage in a template page:
 *   <script src="../../static/vendor/chart.umd.min.js"></script>
 *   <script src="../../static/ufpel-charts.js"></script>
 *
 *   <figure class="chart" data-asset="revenue-chart">
 *     <canvas data-chart height="300"></canvas>
 *     <script type="application/json">
 *       { "type": "bar",
 *         "data": { "labels": ["Q1","Q2"], "datasets": [{ "label": "Revenue", "data": [42, 58] }] } }
 *     </script>
 *   </figure>
 *
 * Datasets without explicit colors get the UFPel palette in order.
 * Put data-theme="dark" on the canvas (or any ancestor) for dark slides.
 * The render pipeline awaits window.__ufpelReady before screenshotting.
 */
(function () {
  // official UFPel palette (identity manual, Padrões Cromáticos):
  // blue 287U, light blue 2915U, orange 021U, ink, green 382U, blue-gray
  const PALETTE = ['#00408F', '#B5DCF1', '#F7A600', '#14202E', '#BCCF00', '#54677D'];
  // dark (navy) surfaces: deep blue and ink vanish — lift them
  const PALETTE_DARK = ['#5FA8E8', '#B5DCF1', '#F7A600', '#FFFFFF', '#BCCF00', '#9FB4C8'];
  const LIGHT = { text: '#14202E', muted: '#54677D', grid: 'rgba(20, 32, 46, 0.08)' };
  const DARK = { text: '#FFFFFF', muted: '#B5DCF1', grid: 'rgba(255, 255, 255, 0.07)' };

  function isDark(el) {
    return Boolean(el.closest('[data-theme="dark"]'));
  }

  function withAlpha(hex, alpha) {
    const n = parseInt(hex.slice(1), 16);
    const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function applyPalette(config, dark) {
    const type = config.type;
    (config.data.datasets || []).forEach(function (ds, i) {
      const pal = dark ? PALETTE_DARK : PALETTE;
      const color = pal[i % pal.length];
      if (type === 'doughnut' || type === 'pie' || type === 'polarArea') {
        ds.backgroundColor =
          ds.backgroundColor ||
          (config.data.labels || []).map(function (_, j) {
            return pal[j % pal.length];
          });
        ds.borderColor = ds.borderColor || (dark ? '#002A5C' : '#FFFFFF');
        ds.borderWidth = ds.borderWidth != null ? ds.borderWidth : 2;
      } else if (type === 'line' || type === 'radar') {
        ds.borderColor = ds.borderColor || color;
        ds.backgroundColor = ds.backgroundColor || withAlpha(color, 0.12);
        ds.pointBackgroundColor = ds.pointBackgroundColor || color;
        ds.borderWidth = ds.borderWidth != null ? ds.borderWidth : 3;
        ds.pointRadius = ds.pointRadius != null ? ds.pointRadius : 3;
        if (ds.fill == null) ds.fill = type === 'line';
        ds.tension = ds.tension != null ? ds.tension : 0.35;
      } else {
        ds.backgroundColor = ds.backgroundColor || color;
        ds.borderRadius = ds.borderRadius != null ? ds.borderRadius : 4;
        ds.maxBarThickness = ds.maxBarThickness != null ? ds.maxBarThickness : 42;
      }
    });
  }

  function themedOptions(config, dark) {
    const t = dark ? DARK : LIGHT;
    const scales = {};
    const wantsScales = !['doughnut', 'pie', 'polarArea', 'radar'].includes(config.type);
    if (wantsScales) {
      ['x', 'y'].forEach(function (axis) {
        scales[axis] = {
          grid: { color: t.grid, drawBorder: false },
          ticks: { color: t.muted, font: { family: 'Montserrat', size: 13 } },
          border: { display: false },
        };
      });
    }
    return {
      responsive: false,
      animation: false,
      // canvases embed as bitmaps in the PDF while everything else is
      // vector — 3x backing store keeps charts print-crisp
      devicePixelRatio: 3,
      plugins: {
        legend: {
          display: (config.data.datasets || []).length > 1 || ['doughnut', 'pie', 'polarArea'].includes(config.type),
          position: 'bottom',
          labels: {
            color: t.text,
            font: { family: 'Montserrat', size: 13, weight: 500 },
            boxWidth: 14,
            boxHeight: 14,
            padding: 16,
          },
        },
        title: { display: false },
        tooltip: { enabled: false },
      },
      scales: scales,
    };
  }

  function deepMerge(base, extra) {
    if (!extra) return base;
    for (const k of Object.keys(extra)) {
      if (
        extra[k] &&
        typeof extra[k] === 'object' &&
        !Array.isArray(extra[k]) &&
        base[k] &&
        typeof base[k] === 'object'
      ) {
        deepMerge(base[k], extra[k]);
      } else {
        base[k] = extra[k];
      }
    }
    return base;
  }

  function domReady() {
    if (document.readyState !== 'loading') return Promise.resolve();
    return new Promise(function (resolve) {
      document.addEventListener('DOMContentLoaded', resolve, { once: true });
    });
  }

  window.__ufpelReady = (async function () {
    // this file loads from <head>: the canvases do not exist yet, and
    // document.fonts.ready can resolve before the body is parsed
    await domReady();
    await document.fonts.ready;
    if (typeof Chart === 'undefined') return;
    Chart.defaults.font.family = 'Montserrat';
    Chart.defaults.font.size = 13;

    document.querySelectorAll('canvas[data-chart]').forEach(function (canvas) {
      const jsonEl = canvas.parentElement.querySelector('script[type="application/json"]');
      if (!jsonEl) return;
      let config;
      try {
        config = JSON.parse(jsonEl.textContent);
      } catch (e) {
        console.error('ufpel-charts: bad JSON config', e);
        return;
      }
      const dark = isDark(canvas);
      // canvas needs explicit pixel size for responsive:false
      if (!canvas.width || canvas.width === 300) {
        canvas.width = canvas.parentElement.clientWidth || 600;
      }
      if (!canvas.getAttribute('height')) canvas.height = 300;
      applyPalette(config, dark);
      config.options = deepMerge(themedOptions(config, dark), config.options);
      new Chart(canvas.getContext('2d'), config);
    });
  })();
})();
