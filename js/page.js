/* The war dead and the rise of Labour: county and borough units of Great Britain shaded by First World War memorial names
 * per 1,000 electors of 1918, or by Labour's vote 1910 to 1924, with memorial places and 1918 seats on a plain MapLibre map
 * (OpenFreeMap Positron). Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:700px)').matches;
  const f1 = v => v == null ? 'n/a' : (+v).toFixed(1);
  const int = v => v == null ? 'n/a' : Math.round(v).toLocaleString('en-GB');
  const SEQ = ['#F3E9DA', '#E3CBB0', '#CFA582', '#B67B58', '#94553A', '#6A3524'], SEQB = [10, 25, 35, 45, 55, 70];
  const RED = ['#FBE9E4', '#F4C2B5', '#E8907C', '#D65A47', '#B4322A', '#7F1D1A'];
  const LABB = [0, 10, 20, 30, 40, 55], GAINB = [-5, 5, 10, 15, 20, 30];
  const EL = { d1910: 'December 1910', e1918: '1918', e1922: '1922', e1923: '1923', e1924: '1924' };
  const st = { mode: 'rate', e: 'e1918' };
  let map, UN, PL, SE, items = [];

  document.getElementById('theme').addEventListener('click', () => { const r = document.documentElement, d = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; r.dataset.theme = d ? 'light' : 'dark'; });
  const ct = document.getElementById('cartouche'); const fold = f => { ct.classList.toggle('folded', f); document.getElementById('ctToggle').setAttribute('aria-expanded', String(!f)); };
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));
  const lp = document.getElementById('lp'), lb = document.getElementById('lyrBtn');
  lb.addEventListener('click', () => { const o = lp.classList.toggle('open'); lb.setAttribute('aria-expanded', String(o)); });

  function step(prop, breaks, cols, maskMain) {
    const e = ['step', ['to-number', ['get', prop]], cols[0]];
    for (let k = 1; k < breaks.length; k++) e.push(breaks[k], cols[k]);
    const base = ['case', ['!', ['has', prop]], '#E4E0D8'];
    if (maskMain) base.push(['==', ['get', 'main'], 0], '#E4E0D8');
    return [...base, e];
  }
  function fillExpr() {
    if (st.mode === 'rate') return step('rate', SEQB, SEQ, true);
    if (st.mode === 'lab') return step(st.e + '_LAB', LABB, RED, false);
    return step('d_lab18', GAINB, RED, true);
  }
  function keys() {
    const k = document.getElementById('keys');
    let t, cols, br, unit;
    if (st.mode === 'rate') { t = 'First World War names per 1,000 electors of 1918'; cols = SEQ; br = SEQB; unit = ''; }
    else if (st.mode === 'lab') { t = `Labour share of the vote, ${EL[st.e]} (%)`; cols = RED; br = LABB; unit = ''; }
    else { t = 'Labour gain, Dec 1910 to 1918 (points)'; cols = RED; br = GAINB; unit = ''; }
    const ld = document.getElementById('lyP').checked, ls = document.getElementById('lyS').checked;
    k.innerHTML = `<b>${t}</b><div class="ramp">${cols.map(c => `<i style="background:${c}"></i>`).join('')}</div><div class="ends"><span>${br[0]}</span><span>${br[2]}</span><span>${br[4]}</span><span>${st.mode === 'rate' ? '140' : (st.mode === 'lab' ? '80' : '60')}</span></div>
      <div class="row"><span class="hatch"></span>${st.mode === 'lab' ? 'no contested seat' : (st.mode === 'rate' ? 'no city-wide count (under 10)' : 'no count or no 1910 contest')}</div>
      ${ld ? '<div class="row"><span class="dot" style="background:#6A3524"></span>memorial place<span class="long">, sized by names per 1,000 residents today (hollow: no population)</span></div>' : ''}
      ${ls ? '<div class="row"><span class="dot" style="background:#B4322A"></span>1918 seat, by Labour share</div>' : ''}
      <div class="nt">Great Britain only<span class="long">. Units: counties, county towns and boroughs</span>.${ld ? '' : '<span class="long"> Memorial places: see Layers.</span>'}</div>`;
  }
  function apply() {
    if (!map || !map.getLayer('units')) return;
    map.setPaintProperty('units', 'fill-color', fillExpr());
    document.getElementById('era').hidden = st.mode !== 'lab';
    keys();
  }
  document.querySelectorAll('[data-mode]').forEach(b => b.addEventListener('click', () => {
    st.mode = b.dataset.mode; document.querySelectorAll('[data-mode]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); apply();
  }));
  document.querySelectorAll('[data-e]').forEach(b => b.addEventListener('click', () => {
    st.e = b.dataset.e; document.querySelectorAll('[data-e]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); apply();
  }));

  const pane = document.getElementById('mapWrap');
  function track(pp) { pane.classList.add('pop'); pp.on('close', () => pane.classList.remove('pop')); return pp; }
  function unitPopup(p, ll) {
    const row = (k, n) => `<tr><td>${n}</td><td>Labour ${f1(p[k + '_LAB'])}%${p[k + '_LIBALL'] != null ? `, Liberal ${f1(p[k + '_LIBALL'])}%` : ''}</td></tr>`;
    track(new maplibregl.Popup({ maxWidth: '330px' })).setLngLat(ll).setHTML(`<b class="t">${esc(p.unit.replace(' (shire)', ''))}</b>
      <div class="nt">${esc(p.region)} · ${int(p.e1918_n_seats)} seat${p.e1918_n_seats === 1 ? '' : 's'} in 1918</div>
      <table><tr><td>Memorial names</td><td><b>${int(p.dead1)}</b> on ${int(p.places_ww1)} of ${int(p.places)} memorial places</td></tr>
      <tr><td>Electors, 1918</td><td>${int(p.elect18)}</td></tr>
      <tr><td>Per 1,000</td><td><b>${f1(p.rate)}</b>${p.main ? '' : ' (no city-wide roll: left out of the main models)'}</td></tr>
      ${p.village_rate != null ? `<tr><td>Villages</td><td>median ${f1(p.village_rate)} names per 1,000 residents today</td></tr>` : ''}
      ${p.d1910_LAB != null ? row('d1910', 'Dec 1910') : '<tr><td>Dec 1910</td><td>no contested seat</td></tr>'}
      ${p.e1918_LAB != null ? row('e1918', '1918') : '<tr><td>1918</td><td>no contested seat</td></tr>'}
      ${p.e1918_COAL != null ? `<tr><td></td><td>Coalition ${f1(p.e1918_COAL)}%, turnout ${f1(p.e1918_turnout)}%</td></tr>` : ''}
      ${p.e1922_LAB != null ? row('e1922', '1922') : ''}
      ${p.e1924_LAB != null ? `<tr><td>1924</td><td>Labour ${f1(p.e1924_LAB)}%</td></tr>` : ''}</table>
      <div class="nt">Shares of the vote in contested seats. Names: IWM War Memorials Register, one community memorial per place.</div>`).addTo(map);
  }
  function placePopup(i, ll) {
    const r = PL.rows[i];
    const [lon, lat, place, dead, title, mid, per, pop, unit, seat] = r;
    track(new maplibregl.Popup({ maxWidth: '320px' })).setLngLat(ll || [lon, lat]).setHTML(`<b class="t">${esc(place)}</b>
      <table><tr><td>Memorial</td><td>${esc(title || 'community memorial')}</td></tr>
      <tr><td>Names</td><td><b>${int(dead)}</b> First World War dead</td></tr>
      ${per != null ? `<tr><td>Per 1,000</td><td>${f1(per)} residents today (modern population)</td></tr>` : ''}
      <tr><td>1918 seat</td><td>${esc(seat)} <span class="nt">(nearest)</span></td></tr>
      <tr><td>Unit</td><td>${esc(String(unit).replace(' (shire)', ''))}</td></tr></table>
      ${mid ? `<div class="nt"><a href="https://www.iwm.org.uk/memorials/item/memorial/${mid}" target="_blank" rel="noopener">War Memorials Register record ${mid}</a></div>` : ''}`).addTo(map);
  }
  function seatPopup(i, ll) {
    const [lon, lat, name, lab, coal, lib, turn, contested, won, unit] = SE.rows[i];
    track(new maplibregl.Popup({ maxWidth: '320px' })).setLngLat(ll || [lon, lat]).setHTML(`<b class="t">${esc(name)}</b>
      <div class="nt">General election, December 1918</div>
      <table>${contested ? `<tr><td>Labour</td><td>${f1(lab)}%</td></tr><tr><td>Coalition</td><td>${f1(coal)}%</td></tr><tr><td>Liberal (all)</td><td>${f1(lib)}%</td></tr><tr><td>Turnout</td><td>${f1(turn)}%</td></tr>` : '<tr><td></td><td>returned unopposed</td></tr>'}
      <tr><td>Elected</td><td>${esc(won)}</td></tr></table>
      <div class="nt">Point placed at the seat's main place: 1918 boundaries are not mapped. Source: UK Parliament general election results (Open Parliament Licence), matched to Wikidata.</div>`).addTo(map);
  }

  function search() {
    const q = document.getElementById('q'), ul = document.getElementById('sug'); let sel = -1, cur = [];
    const go = it => { ul.style.display = 'none'; q.value = it.n; map.flyTo({ center: it.ll, zoom: Math.max(map.getZoom(), it.z) });
      map.once('moveend', () => { if (it.k === 'p') { document.getElementById('lyP').checked = true; vis(); placePopup(it.i); } else if (it.k === 's') { document.getElementById('lyS').checked = true; vis(); seatPopup(it.i); } else unitPopup(it.p, it.ll); }); };
    const show = () => { ul.innerHTML = cur.map((it, j) => `<li role="option" aria-selected="${j === sel}" data-j="${j}">${esc(it.n)} <span>${it.d}</span></li>`).join(''); ul.style.display = cur.length ? 'block' : 'none'; };
    q.addEventListener('input', () => { const v = norm(q.value.trim()); sel = -1; if (v.length < 2) { cur = []; show(); return; }
      const a = [], b = []; for (const it of items) { const n = it.nn; if (n.startsWith(v)) a.push(it); else if (n.includes(v)) b.push(it); if (a.length > 12) break; } cur = a.concat(b).slice(0, 12); show(); });
    q.addEventListener('keydown', e => { if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, cur.length - 1); show(); e.preventDefault(); } else if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); show(); e.preventDefault(); } else if (e.key === 'Enter' && cur.length) go(cur[Math.max(sel, 0)]); else if (e.key === 'Escape') { ul.style.display = 'none'; } });
    ul.addEventListener('click', e => { const li = e.target.closest('li'); if (li) go(cur[+li.dataset.j]); });
  }
  function vis() {
    const set = (ids, on) => ids.forEach(id => map.getLayer(id) && map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none'));
    set(['units'], document.getElementById('lyU').checked);
    set(['units-line'], document.getElementById('lyB').checked);
    set(['places'], document.getElementById('lyP').checked);
    set(['seats'], document.getElementById('lyS').checked);
    map.getStyle().layers.filter(l => l.type === 'symbol' && !['places', 'seats'].includes(l.id)).forEach(l => map.setLayoutProperty(l.id, 'visibility', document.getElementById('lyL').checked ? 'visible' : 'none'));
    keys();
  }
  ['lyU', 'lyB', 'lyP', 'lyS', 'lyL'].forEach(id => document.getElementById(id).addEventListener('change', vis));

  Promise.all(['data/map_units.json', 'data/map_places.json', 'data/map_seats.json'].map(u => fetch(u).then(r => r.json()))).then(([u, p, s]) => {
    UN = u; PL = p; SE = s;
    map = new maplibregl.Map({ container: 'map', style: STYLE, bounds: [[-7.8, 49.9], [1.9, 58.8]], fitBoundsOptions: { padding: small ? 10 : 30 }, attributionControl: { compact: true }, maxZoom: 13, minZoom: 4 });
    window.__map = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    map.on('load', () => {
      document.getElementById('nojs').remove();
      const firstSym = map.getStyle().layers.find(l => l.type === 'symbol');
      map.addSource('units', { type: 'geojson', data: UN });
      map.addLayer({ id: 'units', type: 'fill', source: 'units', paint: { 'fill-color': fillExpr(), 'fill-opacity': ['interpolate', ['linear'], ['zoom'], 5, 0.85, 10, 0.45] } }, firstSym && firstSym.id);
      map.addLayer({ id: 'units-line', type: 'line', source: 'units', paint: { 'line-color': '#FFFFFF', 'line-width': ['interpolate', ['linear'], ['zoom'], 5, 0.6, 10, 2] } }, firstSym && firstSym.id);
      map.addSource('places', { type: 'geojson', data: { type: 'FeatureCollection', features: PL.rows.map((r, i) => ({ type: 'Feature', id: i, geometry: { type: 'Point', coordinates: [r[0], r[1]] }, properties: { i, d: r[3], r: r[6] == null ? 0 : Math.min(r[6], 200) } })) } });
      map.addLayer({ id: 'places', type: 'circle', source: 'places', layout: { 'circle-sort-key': ['-', 0, ['get', 'r']] }, paint: {
        'circle-color': ['case', ['>', ['get', 'r'], 0], '#6A3524', '#FFFFFF'], 'circle-opacity': ['interpolate', ['linear'], ['zoom'], 5, 0.55, 9, 0.8],
        'circle-stroke-color': ['case', ['>', ['get', 'r'], 0], '#FFFFFF', '#6A3524'], 'circle-stroke-width': ['case', ['>', ['get', 'r'], 0], 0.5, 1],
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, ['max', 3, ['*', 0.45, ['sqrt', ['get', 'r']]]], 9, ['max', 3.5, ['*', 1.0, ['sqrt', ['get', 'r']]]], 13, ['max', 5, ['*', 1.8, ['sqrt', ['get', 'r']]]]] } });
      map.addSource('seats', { type: 'geojson', data: { type: 'FeatureCollection', features: SE.rows.map((r, i) => ({ type: 'Feature', geometry: { type: 'Point', coordinates: [r[0], r[1]] }, properties: { i, lab: r[3] == null ? -1 : r[3], c: r[7] } })) } });
      const sc = ['step', ['get', 'lab'], '#BDB6A9', 0, RED[0], 10, RED[1], 20, RED[2], 30, RED[3], 40, RED[4], 55, RED[5]];
      map.addLayer({ id: 'seats', type: 'circle', source: 'seats', layout: { visibility: 'none' }, paint: { 'circle-color': ['case', ['==', ['get', 'c'], 0], '#BDB6A9', sc], 'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, 4, 10, 8], 'circle-stroke-color': '#22201C', 'circle-stroke-width': 1.2 } });
      map.on('click', e => {
        const f = map.queryRenderedFeatures(e.point, { layers: ['seats', 'places', 'units'].filter(l => map.getLayoutProperty(l, 'visibility') !== 'none') });
        if (!f.length) return;
        const a = f[0];
        if (a.layer.id === 'seats') seatPopup(a.properties.i, e.lngLat); else if (a.layer.id === 'places') placePopup(a.properties.i, e.lngLat); else unitPopup(a.properties, e.lngLat);
      });
      ['seats', 'places', 'units'].forEach(l => { map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });
      items = [];
      UN.features.forEach(f => { const p = f.properties; const c = f.geometry.type === 'Polygon' ? f.geometry.coordinates[0] : f.geometry.coordinates[0][0];
        let x = 0, y = 0; c.forEach(q => { x += q[0]; y += q[1]; }); const n = p.unit.replace(' (shire)', '');
        items.push({ k: 'u', n, nn: norm(n), d: 'county or borough', ll: [x / c.length, y / c.length], z: 8, p }); });
      SE.rows.forEach((r, i) => items.push({ k: 's', n: r[2], nn: norm(r[2]), d: '1918 seat', ll: [r[0], r[1]], z: 10, i }));
      PL.rows.forEach((r, i) => items.push({ k: 'p', n: r[2], nn: norm(r[2]), d: `memorial, ${r[3].toLocaleString('en-GB')} names`, ll: [r[0], r[1]], z: 12, i }));
      search(); vis(); apply();
    });
  }).catch(err => { document.getElementById('nojs').textContent = 'The map data could not be loaded.'; console.error(err); });
})();
