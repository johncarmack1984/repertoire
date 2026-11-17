(() => {
'use strict';

// Defined before the page's module runs, so a failed import or any later error rejects `ready` at once.
let resolveReady, rejectReady;
const ready = new Promise((y, n) => { resolveReady = y; rejectReady = n; });
window.dataMap = {ready, report: () => null};
addEventListener('error', e => rejectReady(e.error || new Error(e.message)));
addEventListener('unhandledrejection', e => rejectReady(e.reason));

const NS = 'http://www.w3.org/2000/svg';
const RAD = Math.PI / 180;
const EARTH_KM = 6371;
const NONE = ['==', ['id'], '__dm_none__'];
// MapLibre hits a line only within half its width, which leaves a hairline flow all but untappable, so an unseen line
// at least this wide, in px, takes the pointer under each flow; a finger lands less exactly than a mouse.
const HIT = matchMedia('(pointer: coarse)').matches ? 24 : 12;
const ARROW = {len: 20, base: 19, pad: 4};
const ARC_APEX = 0.08;
const FRAME = 'none';
const METHOD = {quantile: k => `${k} quantile classes`, jenks: k => `${k} classes by natural breaks (Jenks)`,
  equal: k => `${k} equal-interval classes`, stddev: k => `${k} classes by standard deviation from the mean`,
  headtail: k => `${k} classes by head/tail breaks`, geometric: k => `${k} classes in a constant ratio`, manual: k => `${k} classes set by hand`};
// Slocum's order of label positions (§12.5.2): the corner of the name that touches the point, and the way the name runs from it.
const CORNERS = [['bottom-left', 1, -1], ['top-left', 1, 1], ['bottom-right', -1, -1], ['top-right', -1, 1],
  ['bottom', 0, -1], ['top', 0, 1], ['left', 1, 0], ['right', -1, 0]];
const POLYGONS = ['match', ['geometry-type'], ['Polygon', 'MultiPolygon'], true, false];
const LINES = ['match', ['geometry-type'], ['LineString', 'MultiLineString'], true, false];

const $ = id => document.getElementById(id);
const parse = id => { const e = $(id); return e ? JSON.parse(e.textContent) : null; };
const spec = parse('dm-spec') || {};
const stems = [...document.querySelectorAll('script[id^="dm-data-"]')].map(e => e.id.slice(8));
const data = Object.fromEntries(stems.map(s => [s, parse('dm-data-' + s)]));
const legend = data.legend || {layers: {}};
const layersOf = () => Object.entries(legend.layers || {});
// MapLibre drops a GeoJSON feature's string id, which the levers write for areas and symbols, so each feature carries
// its key as dm_key, as flow nodes do already.
for (const fc of Object.values(data)) {
  for (const f of fc?.type === 'FeatureCollection' ? fc.features : []) if (f.properties && f.properties.dm_key == null && typeof f.id === 'string') f.properties.dm_key = f.id;
}
// The largest dm_rank each flows layer draws, for a layer whose lever wrote more flows than it draws at load
// (flows --reveal); the reveal control moves it.
const ranks = Object.fromEntries(layersOf().filter(([, L]) => L.kind === 'flows' && L.reveal?.count > 0).map(([name, L]) => [name, L.reveal.default]));
// With "focus" in dm-spec.controls, the reader picks one node of one flows layer, and that layer draws only the flows
// to and from it, every one its file holds; focused is {layer, key} then, and null on the overview.
const focusLayer = (spec.controls || []).includes('focus')
  ? spec.focus?.layer ?? layersOf().find(([, L]) => L.kind === 'flows')?.[0] ?? null : null;
let focused = null;
const touches = (p, key) => p.dm_o === key || p.dm_d === key;
const drawnFlow = (name, p) => focused?.layer === name ? touches(p, focused.key) : !(p.dm_rank > (ranks[name] ?? Infinity));
const lineFilter = name => focused?.layer === name ? ['any', ['==', ['get', 'dm_o'], focused.key], ['==', ['get', 'dm_d'], focused.key]]
  : ranks[name] != null ? ['<=', ['coalesce', ['get', 'dm_rank'], 0], ranks[name]] : null;
// With a reveal, the nodes file holds the ends of every written flow, and the page draws only the ends of the flows
// it draws: per flows layer, the keys of those nodes.
const shownKeys = {};
function updateShownKeys(name) {
  const keys = shownKeys[name] = new Set();
  for (const {properties: p} of data[filesOf(name, legend.layers[name]).main]?.features || []) {
    if (drawnFlow(name, p)) { keys.add(p.dm_o); keys.add(p.dm_d); }
  }
}
const nodeFilter = name => ['in', ['get', 'dm_key'], ['literal', [...shownKeys[name]]]];
function nodeHidden(source, f) {
  const name = Object.keys(shownKeys).find(n => filesOf(n, legend.layers[n]).nodes === source);
  return name != null && !shownKeys[name].has(f.properties.dm_key ?? f.id);
}
// What the page holds once the map exists, for controls that change it.
const live = {};
const tok = name => getComputedStyle(document.documentElement).getPropertyValue('--dm-' + name).trim();
const fontStack = () => tok('font').split(',').map(s => s.trim().replace(/^["']|["']$/g, ''));
const fmt = v => v == null || v === '' ? '' : typeof v === 'number'
  ? v.toLocaleString(spec.locale || 'en-US', {maximumFractionDigits: Math.abs(v) < 10 ? 1 : 0}) : String(v);
const stemOf = f => String(f).replace(/^data\//, '').replace(/\.(geo)?json$/, '');
const filesOf = (name, L = {}) => {
  const f = L.files || {};
  return {main: stemOf(f.lines || name), nodes: stemOf(f.nodes || name + '-nodes'), arrows: stemOf(f.arrows || name + '-arrows')};
};

function html(tag, attrs = {}, parent, text) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  parent?.append(e);
  return e;
}
function svg(tag, attrs = {}, parent, text) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  parent?.append(e);
  return e;
}
function label(parent, x, y, text, attrs = {}) {
  return svg('text', {x, y, dy: '0.35em', ...attrs}, parent, text);
}
function mark(e, layer, kind, color, text, expect) {
  Object.assign(e.dataset, {dmLayer: layer, dmKind: kind, dmColor: color, dmLabel: text ?? '', dmExpect: expect ? '1' : '0'});
}
let pageLibs = {};
let measurer;
function measure(text, bold = false) {
  measurer ??= document.createElement('canvas').getContext('2d');
  measurer.font = `${bold ? '700 ' : ''}${tok('t4')} ${tok('font')}`;
  return measurer.measureText(String(text)).width;
}

// The places dm-spec.highlight names, by node or feature key: the ones the title is about. Their names draw bold and
// their circles or areas outlined, on the map and in the companions that name them.
const highlighted = new Set((spec.highlight || []).map(String));
const keyOf = f => String(f.properties?.dm_key ?? f.id);
const isHighlighted = ['in', ['get', 'dm_key'], ['literal', [...highlighted]]];
// Each highlighted key's name, from whichever layer holds it.
function highlightNames() {
  const out = new Map();
  for (const [name, L] of layersOf()) {
    const stem = L.kind === 'flows' ? filesOf(name, L).nodes : name;
    for (const f of data[stem]?.features || []) if (highlighted.has(keyOf(f))) out.set(keyOf(f), String(f.properties.dm_label ?? keyOf(f)));
  }
  return out;
}
// The highlighted key a companion row names, by its whole label or its key.
function rowHighlight(label) {
  const said = String(label ?? '').trim().toLowerCase();
  for (const [key, name] of highlightNames()) if (said === name.toLowerCase() || said === key.toLowerCase()) return key;
  return null;
}
// A circle's outline: the page color, or the text color, thicker, around a highlighted place.
const ring = (t, width) => highlighted.size
  ? {'circle-stroke-color': ['case', isHighlighted, t.text, t.page], 'circle-stroke-width': ['case', isHighlighted, 2, width]}
  : {'circle-stroke-color': t.page, 'circle-stroke-width': width};
function fit(text, width, bold = false) {
  text = String(text);
  if (measure(text, bold) <= width) return text;
  while (text.length > 1 && measure(text + '…', bold) > width) text = text.slice(0, -1);
  return text + '…';
}
// SVG text never wraps, so a legend line longer than the panel breaks into lines here.
function wrap(text, width) {
  const out = [];
  for (const word of String(text).split(' ')) {
    const longer = out.length ? `${out[out.length - 1]} ${word}` : word;
    if (out.length && measure(longer) <= width) out[out.length - 1] = longer;
    else out.push(word);
  }
  return out;
}
const rgb = hex => { const h = hex.replace('#', ''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };

// ---------- legend ----------

const LEGENDS = {
  classes(sec, name, L) {
    const colors = L.colors || [], labels = L.labels || [], counts = L.counts || [];
    const sw = 26, sh = 14, gap = 8;
    const extra = [];
    if (L.nodata) extra.push({kind: 'nodata', color: L.nodata.color, text: L.nodata.label || 'No data', expect: (L.nodata.count || 0) > 0});
    if (L.low_n?.count > 0) extra.push({kind: 'low-n', hatch: true,
      text: L.low_n.label || `Hatched: fewer than ${fmt(L.low_n.threshold)} in the denominator`});
    const line = parseFloat(tok('t4')) * 1.25, width = sec.getBoundingClientRect().width || parseFloat(tok('side'));
    // A narrow figure is short of height, so its swatches run across, touching, low on the left, each class's
    // lower limit below its left edge (Slocum §14.7); the side panel is short of width, so its swatches stack.
    const across = document.body.classList.contains('dm-narrow'), cell = Math.min(64, width / Math.max(colors.length, 1));
    const top = (across ? sh + line + 4 : colors.length * sh) + (extra.length ? 10 : 0);
    const room = width - sw - gap;
    let y = top;
    for (const x of extra) {
      x.lines = wrap(x.text, room);
      x.y = y;
      y += Math.max(sh, x.lines.length * line) + 6;
    }
    const s = svg('svg', {width: '100%', height: y}, sec);
    const pattern = svg('pattern', {id: `dm-hatch-${name}`, width: 6, height: 6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)'}, svg('defs', {}, s));
    svg('line', {x1: 0, y1: 0, x2: 0, y2: 6, stroke: 'rgba(40,40,40,0.3)', 'stroke-width': 1.2}, pattern);
    colors.forEach((c, i) => {
      if (across) {
        mark(svg('rect', {x: i * cell, y: 0, width: cell, height: sh, fill: c}, s), name, 'class', c, labels[i], (counts[i] ?? 1) > 0);
        const low = String(labels[i] ?? '').match(/^-?[\d,.]+/)?.[0] ?? '';
        label(s, i * cell, sh + line / 2 + 2, low, i ? {'text-anchor': 'middle'} : {});
        const high = i === colors.length - 1 && String(labels[i] ?? '').match(/ to (-?[\d,.]+)$/)?.[1];
        if (high) label(s, (i + 1) * cell, sh + line / 2 + 2, high, {'text-anchor': 'end'});
      } else {
        mark(svg('rect', {x: 0, y: i * sh, width: sw, height: sh, fill: c}, s), name, 'class', c, labels[i], (counts[i] ?? 1) > 0);
        label(s, sw + gap, i * sh + sh / 2, labels[i] ?? '');
      }
    });
    for (const x of extra) {
      const y = x.y;
      if (x.hatch) {
        svg('rect', {x: 0, y, width: sw, height: sh, fill: tok('page'), stroke: tok('rule'), 'stroke-width': 0.5}, s);
        svg('rect', {x: 0, y, width: sw, height: sh, fill: `url(#dm-hatch-${name})`}, s);
      } else {
        mark(svg('rect', {x: 0, y, width: sw, height: sh, fill: x.color}, s), name, x.kind, x.color, x.text, x.expect);
      }
      x.lines.forEach((text, i) => label(s, sw + gap, y + sh / 2 + i * line, text));
    }
    if (L.method) html('p', {class: 'dm-note'}, sec, (METHOD[L.method] || (k => `${k} classes, ${L.method}`))(L.k || colors.length));
  },
  sizes(sec, name, L) {
    nested(sec, name, L.legend_values || [], L.legend_radii || [], L.color || firstFill(name) || tok('symbol'));
  },
  flows(sec, name, L) {
    const values = L.legend_values || [], widths = L.legend_widths || [], alphas = L.legend_opacities || [];
    const color = L.color || firstFill(filesOf(name, L).main) || tok('flow');
    const head = w => Math.max((L.arrow?.ratio ?? 2.5) * w, L.arrow?.min_px ?? 6);
    const run = 44, longest = Math.max(0, ...widths.map(head));
    const rows = widths.map((w, i) => ({w, v: values[i], a: alphas[i] ?? 1, len: head(w), h: Math.max(head(w) * ARROW.base / ARROW.len, 12)}));
    const s = svg('svg', {width: '100%', height: rows.reduce((a, r) => a + r.h + 6, 0)}, sec);
    let y = 0;
    for (const r of rows) {
      const cy = y + r.h / 2, half = r.len * ARROW.base / ARROW.len / 2;
      mark(svg('line', {x1: 0, x2: run + 0.5, y1: cy, y2: cy, stroke: color, 'stroke-width': r.w, 'stroke-opacity': r.a}, s), name, 'flow', color, fmt(r.v), true);
      svg('polygon', {points: `${run},${cy - half} ${run + r.len},${cy} ${run},${cy + half}`, fill: color}, s);
      label(s, run + longest + 10, cy, fmt(r.v));
      y += r.h + 6;
    }
    const kept = overviewNote(name, L);
    const note = kept ? html('p', {class: 'dm-note', id: `dm-kept-${name}`}, sec, kept) : null;
    if (note && ranks[name] != null && (spec.controls || []).includes('reveal')) revealControl(sec, name, L, note);
    if (pageLibs.deck && (spec.arcs?.apex ?? ARC_APEX) > 0) html('p', {class: 'dm-note'}, sec, `Arc height shows distance, not ${L.unit || 'size'}.`);
    const nodes = data[filesOf(name, L).nodes]?.features || [], N = L.nodes || {}, unit = L.unit || 'flows';
    const size = n => Math.abs(n.properties.dm_value || 0), sized = nodes.filter(n => n.properties.dm_r > 0 && size(n) > 0);
    if (sized.length > 1) {
      html('h3', {}, sec, N.title || NODE_TITLES[N.value || 'gross'](unit));
      const top = sized.reduce((a, n) => size(n) > size(a) ? n : a);
      const rmax = top.properties.dm_r, vmax = size(top);
      const values = N.legend_values || niceSteps(vmax);
      const radii = N.legend_radii || values.map(v => rmax * Math.sqrt(v / vmax));
      // In a net mode the fill says gain or loss, so the size key is drawn as outlines and the two colors get a key.
      const net = N.value === 'net' && N.colors;
      nested(sec, name + '-nodes', values, radii, net ? null : top.properties.dm_fill || tok('node'));
      if (net) signs(sec, name + '-nodes', N.colors, unit, nodes);
    }
  }
};

const NODE_TITLES = {gross: u => `Circle area: all ${u} in and out`, in: u => `Circle area: ${u} arriving`,
  out: u => `Circle area: ${u} leaving`, net: u => `Circle area: all ${u} in and out`};

function signs(sec, layer, colors, unit, nodes) {
  const has = sign => nodes.some(n => Math.sign(n.properties.dm_net || 0) === sign);
  const step = parseFloat(tok('t4')) * 1.7, s = svg('svg', {width: '100%', height: 2 * step}, sec);
  [[colors.gain, `More ${unit} in than out`, has(1)], [colors.loss, `More ${unit} out than in`, has(-1)]].forEach(([c, text, on], i) => {
    mark(svg('circle', {cx: 7, cy: (i + 0.5) * step, r: 6, fill: c, stroke: tok('page'), 'stroke-width': 0.75}, s), layer, 'sign', c, text, on);
    label(s, 22, (i + 0.5) * step, text);
  });
}

// "The 40 largest of 380 flows, 63% of all trips", for the N largest. The lever's kept_share is its default cut's share
// of every flow, so the whole comes back even when the lever wrote fewer flows than there are.
function keptNote(name, L, n) {
  const lines = data[filesOf(name, L).main]?.features || [], total = L.total ?? L.reveal.count;
  const sum = k => lines.reduce((a, f) => a + (f.properties.dm_rank <= k ? f.properties.dm_value || 0 : 0), 0);
  const all = L.kept_share > 0 ? sum(L.reveal.default) / L.kept_share : sum(Infinity);
  if (n >= total) return `All ${fmt(total)} flows`;
  return `The ${n === 1 ? '' : fmt(n) + ' '}largest of ${fmt(total)} flows, ${Math.round(100 * sum(n) / all)}% of all ${L.unit || 'flows'}`;
}

const overviewNote = (name, L) => ranks[name] != null ? keptNote(name, L, ranks[name]) : L.omitted_note;

// A slider that draws the N largest flows. It moves nothing on its own; the kept line under it reads out each value.
function revealControl(sec, name, L, note) {
  const id = `dm-reveal-${name}`, box = html('div', {class: 'dm-reveal', 'data-dm-control': 'reveal'});
  sec.insertBefore(box, note);
  html('label', {for: id}, box, 'Flows drawn, largest first');
  const input = html('input', {type: 'range', id, min: 1, max: L.reveal.count, step: 1, value: ranks[name],
    'aria-describedby': note.id, 'aria-valuetext': note.textContent}, box);
  input.addEventListener('input', () => {
    setRank(name, Number(input.value));
    note.textContent = keptNote(name, L, ranks[name]);
    input.setAttribute('aria-valuetext', note.textContent);
  });
  input.addEventListener('change', () => replaceNames());
}

function setRank(name, n) {
  ranks[name] = n;
  applyView();
}

// Draws what ranks and focused say: each flows layer's lines, heads, nodes, and names, the focused layer's colors,
// and the deck.gl arcs.
function applyView() {
  Object.keys(shownKeys).forEach(updateShownKeys);
  const {map, t} = live;
  if (!map) return;
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows') continue;
    for (const id of [name, name + '-hit', name + '-arrows']) if (map.getLayer(id)) map.setFilter(id, lineFilter(name));
    if (shownKeys[name]) for (const id of [name + '-nodes', name + '-labels']) if (map.getLayer(id)) map.setFilter(id, nodeFilter(name));
    const on = focused?.layer === name, color = on ? focusColor(focused.key) : ['coalesce', ['get', 'dm_fill'], L.color || t.flow];
    if (map.getLayer(name)) map.setPaintProperty(name, 'line-color', color);
    if (map.getLayer(name + '-arrows')) map.setPaintProperty(name + '-arrows', 'icon-color', color);
    if (map.getLayer(name + '-nodes')) {
      const base = ring(t, 1), mine = ['==', ['get', 'dm_key'], on ? focused.key : '__dm_none__'];
      map.setPaintProperty(name + '-nodes', 'circle-stroke-color', ['case', mine, t.text, base['circle-stroke-color']]);
      map.setPaintProperty(name + '-nodes', 'circle-stroke-width', ['case', mine, 2.5, base['circle-stroke-width']]);
    }
  }
  if (live.overlay) {
    live.arcs = arcLayers(pageLibs.deck, t, live.show);
    live.overlay.setProps({layers: live.arcs.map(a => a.layer)});
  }
}

// Once the flows drawn change, the names and notes find their places again, one pass at a time.
let placing = Promise.resolve();
function replaceNames() {
  placing = placing.then(async () => {
    if (!live.map || !labelPlan) return;
    await placeLabels(live.map, labelPlan.labels, labelPlan.deck);
    placeNotes(live.map);
  });
  return placing;
}

function firstFill(stem) {
  return data[stem]?.features?.find(f => f.properties?.dm_fill)?.properties.dm_fill;
}
function niceSteps(vmax) {
  const nice = v => { const p = 10 ** Math.floor(Math.log10(v)); return Math.floor(v / p) * p; };
  return [...new Set([nice(vmax), nice(vmax / 4), nice(vmax / 16)])].filter(v => v > 0);
}
function niceCeil(v) {
  if (!(v > 0)) return 1;
  const p = 10 ** Math.floor(Math.log10(v));
  return [1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10].map(m => m * p).find(x => x >= v);
}
function nested(sec, layer, values, radii, color) {
  if (!values.length) return;
  const fill = color ? {fill: color, stroke: tok('page'), 'stroke-width': 0.75} : {fill: 'none', stroke: tok('muted'), 'stroke-width': 0.75};
  const rmax = Math.max(...radii), cx = rmax + 1, lx = 2 * rmax + 18, step = parseFloat(tok('t4')) + 2;
  const rows = values.map((v, i) => ({v, r: radii[i]})).sort((a, b) => b.r - a.r);
  let base = 2 * rmax + 2;
  // Labels sit at each circle's top, pushed apart where small circles crowd them, with a leader to each top.
  rows.forEach((row, i) => { row.y = Math.max(base - 2 * row.r, i ? rows[i - 1].y + step : -Infinity); });
  const below = Math.max(0, rows.at(-1).y + step / 2 - base);
  const s = svg('svg', {width: '100%', height: base + below + 2}, sec);
  for (const {v, r, y} of rows) {
    mark(svg('circle', {cx, cy: base - r, r, ...fill}, s), layer, 'size', color || tok('muted'), fmt(v), !!color);
    svg('polyline', {points: `${cx},${base - 2 * r} ${lx - 10},${base - 2 * r} ${lx - 4},${y}`, fill: 'none', stroke: tok('muted'), 'stroke-width': 0.5}, s);
    label(s, lx, y, fmt(v));
  }
}

function drawLegend() {
  const box = $('dm-legend');
  if (!box) return;
  box.replaceChildren();
  for (const [name, L] of layersOf()) {
    if (!LEGENDS[L.kind]) continue;
    const sec = html('section', {class: 'dm-legend-layer'}, box);
    html('h2', {}, sec, L.title || name);
    LEGENDS[L.kind](sec, name, L);
  }
}

// ---------- companions: small SVG charts beside the map, or in place of it ----------

function rowsOf(c) {
  if (c.data) {
    const d = data[stemOf(c.data)] || {};
    return {unit: d.unit, columns: d.columns,
      rows: (d.rows || []).map(r => Array.isArray(r) ? {label: r[0], value: r[1], cells: r} : r)};
  }
  const L = legend.layers?.[c.layer] || {};
  const fc = data[filesOf(c.layer, L).main];
  return {unit: L.unit, rows: (fc?.features || []).filter(f => f.properties.dm_value != null)
    .map(f => ({label: f.properties.dm_label ?? f.id, value: f.properties.dm_value}))};
}

const CHARTS = {
  bars(sec, c) {
    const rows = rowsOf(c).rows.slice().sort((a, b) => c.order === 'asc' ? a.value - b.value : b.value - a.value).slice(0, c.top || 10);
    const W = sec.clientWidth || 272, bh = spec.projection ? 13 : 18, gap = spec.projection ? 5 : 6;
    const labelW = Math.min(W * 0.42, Math.max(...rows.map(r => measure(r.label, !!rowHighlight(r.label)))) + 8);
    const valueW = Math.max(...rows.map(r => measure(fmt(r.value)))) + 6;
    const scale = (W - labelW - valueW) / Math.max(...rows.map(r => r.value), 1e-9);
    const s = svg('svg', {width: W, height: rows.length * (bh + gap) - gap}, sec);
    rows.forEach((r, i) => {
      const y = i * (bh + gap), w = Math.max(r.value * scale, 1);
      const hi = rowHighlight(r.label);
      label(s, labelW - 8, y + bh / 2, fit(r.label, labelW - 8, !!hi), {'text-anchor': 'end', ...(hi && {class: 'dm-hi', 'data-dm-highlight': hi})});
      svg('rect', {x: labelW, y, width: w, height: bh, fill: hi ? tok('text') : tok('chart')}, s);
      label(s, labelW + w + 4, y + bh / 2, fmt(r.value));
    });
  },
  table(sec, c) {
    const {rows, columns, unit} = rowsOf(c);
    const cols = columns || ['', unit || ''];
    const body = (c.top ? rows.slice(0, c.top) : rows).map(r => r.cells || [r.label, r.value]);
    const t = html('table', {class: 'dm-table'}, sec);
    const tr = html('tr', {}, html('thead', {}, t));
    const numeric = cols.map((_, i) => body.length > 0 && body.every(r => typeof r[i] === 'number'));
    cols.forEach((h, i) => html('th', numeric[i] ? {class: 'dm-num'} : {}, tr, h));
    const tb = html('tbody', {}, t);
    for (const r of body) {
      const row = html('tr', {}, tb);
      const hi = rowHighlight(r[0]);
      if (hi) Object.assign(row, {className: 'dm-hi'}).dataset.dmHighlight = hi;
      r.forEach((v, i) => html('td', numeric[i] ? {class: 'dm-num'} : {}, row, fmt(v)));
    }
  },
  matrix(sec, c) {
    const L = legend.layers?.[c.layer] || {}, f = filesOf(c.layer, L);
    const lines = data[f.main]?.features || [], nodes = data[f.nodes]?.features || [];
    const names = Object.fromEntries(nodes.map(n => [n.properties.dm_key ?? n.id, n.properties.dm_label ?? n.id]));
    const out = {}, inn = {}, cell = {};
    for (const l of lines) {
      const {dm_o: o, dm_d: d, dm_value: v} = l.properties;
      out[o] = (out[o] || 0) + v; inn[d] = (inn[d] || 0) + v; cell[o + '\u0000' + d] = v;
    }
    const n = c.top || 8;
    const rows = Object.keys(out).sort((a, b) => out[b] - out[a]).slice(0, n);
    const W = sec.clientWidth || 272, labelW = Math.min(W * 0.4, Math.max(...rows.map(r => measure(names[r] ?? r))) + 8);
    const ranked = Object.keys(inn).sort((a, b) => inn[b] - inn[a]);
    const size = Math.min(26, Math.max(20, Math.max(...ranked.slice(0, n).map(d => measure(d))) + 8)), head = 16;
    const cols = ranked.slice(0, Math.min(n, Math.floor((W - labelW) / size)));
    const vmax = Math.max(...Object.values(cell), 1e-9);
    const s = svg('svg', {width: W, height: head + rows.length * size}, sec);
    const ink = firstFill(f.main) || tok('flow');
    cols.forEach((d, j) => label(s, labelW + j * size + size / 2, head / 2, d, {'text-anchor': 'middle', class: 'dm-muted'}));
    rows.forEach((o, i) => {
      label(s, labelW - 8, head + i * size + size / 2, fit(names[o] ?? o, labelW - 8), {'text-anchor': 'end'});
      cols.forEach((d, j) => {
        const v = cell[o + '\u0000' + d], x = labelW + j * size, y = head + i * size;
        svg('rect', v ? {x: x + 1, y: y + 1, width: size - 2, height: size - 2, fill: ink, 'fill-opacity': 0.12 + 0.88 * v / vmax}
          : {x: x + 1, y: y + 1, width: size - 2, height: size - 2, fill: 'none', stroke: tok('rule'), 'stroke-width': 0.5}, s);
      });
    });
    html('p', {class: 'dm-note'}, sec, c.note ?? 'Rows are origins, columns destinations; darker is more.');
  },
  series(sec, c) {
    const d = data[stemOf(c.data)] || {x: [], series: []};
    const all = d.series.flatMap(s => s.values).filter(v => v != null);
    const lo = Math.min(0, ...all), hi = niceCeil(Math.max(...all));
    const nameW = Math.max(...d.series.map(s => measure(s.name))) + 8;
    const W = sec.clientWidth || 272, H = c.height || 120, left = Math.max(measure(fmt(hi)), measure(fmt(lo))) + 6, top = 6, bottom = 16;
    const x = i => left + i * (W - left - nameW) / Math.max(d.x.length - 1, 1);
    const y = v => top + (H - top - bottom) * (1 - (v - lo) / (hi - lo || 1));
    const s = svg('svg', {width: W, height: H}, sec);
    for (const v of [lo, hi]) {
      svg('line', {x1: left, x2: W - nameW, y1: y(v), y2: y(v), stroke: tok('rule'), 'stroke-width': 0.5}, s);
      label(s, left - 4, y(v), fmt(v), {'text-anchor': 'end', class: 'dm-muted'});
    }
    label(s, left, H - 6, d.x[0], {class: 'dm-muted'});
    label(s, W - nameW, H - 6, d.x.at(-1), {'text-anchor': 'end', class: 'dm-muted'});
    d.series.forEach((ser, k) => {
      const pts = ser.values.map((v, i) => v == null ? null : [x(i), y(v)]).filter(Boolean);
      const color = k === 0 ? (c.color || tok('flow')) : tok('chart');
      svg('polyline', {points: pts.map(p => p.join(',')).join(' '), fill: 'none', stroke: color, 'stroke-width': k === 0 ? 2 : 1.25}, s);
      label(s, pts.at(-1)[0] + 4, pts.at(-1)[1], ser.name, {fill: color});
    });
  }
};

function drawCompanions() {
  const box = $('dm-companions');
  if (!box) return;
  box.replaceChildren();
  for (const c of spec.companions || []) {
    const sec = html('section', {class: 'dm-companion'}, box);
    if (c.title) html('h2', {}, sec, c.title);
    if (!CHARTS[c.type]) throw new Error(`dm-spec companion type "${c.type}" is not one of ${Object.keys(CHARTS).join(', ')}`);
    CHARTS[c.type](sec, c);
  }
}

// ---------- map images: an SDF arrowhead that points up with its tip ARROW.pad below the top, and a hatch ----------

function arrowImage() {
  const r = 2, len = ARROW.len * r, base = ARROW.base * r, pad = ARROW.pad * r;
  const w = Math.ceil(base + 2 * pad), h = Math.ceil(len + 2 * pad);
  const pts = [[w / 2, pad], [w / 2 + base / 2, pad + len], [w / 2 - base / 2, pad + len]];
  const edges = pts.map((a, i) => {
    const b = pts[(i + 1) % 3], dx = b[0] - a[0], dy = b[1] - a[1], n = Math.hypot(dx, dy);
    return [a, [dy / n, -dx / n]];
  });
  const px = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const d = Math.max(...edges.map(([a, nrm]) => (x + 0.5 - a[0]) * nrm[0] + (y + 0.5 - a[1]) * nrm[1]));
    px[(y * w + x) * 4 + 3] = Math.round(255 * (0.75 - d / 8));
  }
  return {width: w, height: h, data: px};
}
function hatchImage() {
  const s = 24, px = new Uint8ClampedArray(s * s * 4);
  for (let y = 0; y < s; y++) for (let x = 0; x < s; x++) {
    if ((x + y) % 12 < 2) px.set([40, 40, 40, 70], (y * s + x) * 4);
  }
  return {width: s, height: s, data: px};
}
const IMAGES = {'dm-arrow': [arrowImage, {pixelRatio: 2, sdf: true}], 'dm-hatch': [hatchImage, {pixelRatio: 2}]};

// ---------- map layers, one builder per legend kind ----------

function prepArrows(fc, sideways) {
  for (const f of fc.features) {
    const p = f.properties, size = (p.dm_arrow || 8) / ARROW.len;
    p.dm_icon_size = size;
    // A head follows its line's dm_offset to the right of travel; a deck.gl arc has no offset and lands on the node.
    p.dm_icon_offset = [sideways ? (p.dm_offset || 0) / size : 0, -ARROW.pad + ((p.dm_setback || 0) + 1) / size];
    p.dm_screen = p.dm_bearing;
  }
}

// A name wider than LABEL_EMS breaks at the space that leaves its two lines most even. The page breaks names itself,
// with MapLibre's own wrapping off, so it knows each name's box before placing it; MapLibre wraps at 10 ems by default,
// and a box measured as one line put the second line under the neighbors and off the frame.
const LABEL_EMS = 10;
function breakName(text) {
  text = String(text);
  const words = text.split(' ');
  if (measure(text) <= LABEL_EMS * parseFloat(tok('t4')) || words.length < 2) return text;
  let best = null;
  for (let i = 1; i < words.length; i++) {
    const a = words.slice(0, i).join(' '), b = words.slice(i).join(' '), w = Math.max(measure(a), measure(b));
    if (!best || w < best.w) best = {w, text: `${a}\n${b}`};
  }
  return best.text;
}

function labelLayer(id, source, t) {
  const size = parseFloat(tok('t4'));
  (data[source]?.features || []).forEach((f, i) => {
    f.properties.dm_lid = i;
    if (f.properties.dm_label != null) f.properties.dm_text = breakName(f.properties.dm_label);
  });
  // Slocum's first corner for every name until placeLabels gives each its own. MapLibre takes the weight from the first
  // family's name, so a family no system has carries Bold, and the page's own stack draws the letters.
  const font = highlighted.size ? ['case', isHighlighted, ['literal', ['DataMap Bold', ...fontStack()]], ['literal', fontStack()]] : fontStack();
  return {id, type: 'symbol', source,
    layout: {'text-field': ['get', 'dm_text'], 'text-font': font, 'text-size': size, 'text-max-width': 100, 'text-justify': 'auto',
      'text-anchor': 'bottom-left', 'text-radial-offset': ['+', 0.25, ['/', ['coalesce', ['get', 'dm_r'], 3], size]],
      'symbol-sort-key': ['get', 'dm_order']},
    paint: {'text-color': t.text, 'text-halo-color': t.page, 'text-halo-width': 1.25}};
}

function buildKinds(t, crs, deck) {
  const ink = color => ['coalesce', ['get', 'dm_fill'], color];
  return {
    classes(name, L) {
      const fc = data[name];
      if (!fc) return {};
      const nodata = L.nodata?.color || t.land;
      const fill = ['case', ['==', ['get', 'dm_class'], -1], nodata, ['coalesce', ['get', 'dm_fill'], nodata]];
      const polys = fc.features.some(f => /Polygon/.test(f.geometry?.type));
      if (!polys) return {sources: {[name]: fc}, hover: [[name, name + '-hover']], point: [
        {id: name, type: 'circle', source: name, paint: {'circle-radius': 4.5, 'circle-pitch-scale': 'viewport', 'circle-color': fill, ...ring(t, 0.75)}},
        {id: name + '-hover', type: 'circle', source: name, filter: NONE, paint: {'circle-radius': 4.5, 'circle-pitch-scale': 'viewport', 'circle-opacity': 0, 'circle-stroke-color': t.text, 'circle-stroke-width': 1.5}}]};
      return {sources: {[name]: fc}, hover: [[name, name + '-hover']], fill: [
        {id: name, type: 'fill', source: name, paint: {'fill-color': fill}},
        {id: name + '-low-n', type: 'fill', source: name, filter: ['==', ['get', 'dm_low_n'], true], paint: {'fill-pattern': 'dm-hatch'}},
        // On the bare page a white edge would leave the palest class with no coast, so the edges turn light gray.
        {id: name + '-edge', type: 'line', source: name, paint: {'line-color': crs && frameOf() === 'none' ? t.rule : t.page, 'line-width': 0.5}},
        // A dark line alone vanishes on the darkest class, so it runs on a page-colored casing.
        ...(highlighted.size ? [{id: name + '-highlight-casing', type: 'line', source: name, filter: isHighlighted, paint: {'line-color': t.page, 'line-width': 3.5}},
          {id: name + '-highlight', type: 'line', source: name, filter: isHighlighted, paint: {'line-color': t.text, 'line-width': 1.25}}] : []),
        {id: name + '-hover', type: 'line', source: name, filter: NONE, paint: {'line-color': t.text, 'line-width': 1.5}}]};
    },
    sizes(name, L) {
      const fc = data[name];
      if (!fc) return {};
      return {sources: {[name]: fc}, hover: [[name, name + '-hover']], label: [labelLayer(name + '-labels', name, t)], point: [
        {id: name, type: 'circle', source: name, layout: {'circle-sort-key': ['get', 'dm_order']},
          paint: {'circle-radius': ['get', 'dm_r'], 'circle-pitch-scale': 'viewport', 'circle-color': ink(L.color || t.symbol), ...ring(t, 0.75)}},
        {id: name + '-hover', type: 'circle', source: name, filter: NONE,
          paint: {'circle-radius': ['get', 'dm_r'], 'circle-pitch-scale': 'viewport', 'circle-opacity': 0, 'circle-stroke-color': t.text, 'circle-stroke-width': 1.5}}]};
    },
    flows(name, L) {
      const f = filesOf(name, L), lines = data[f.main], nodes = data[f.nodes], arrows = data[f.arrows];
      const part = {sources: {}, hover: [], line: [], point: [], arrow: [], label: []};
      const color = ink(L.color || t.flow);
      if (lines && !deck) {
        part.sources[f.main] = lines;
        part.line.push(
          // Under the drawn lines, so a pointer on a drawn line takes that line before a neighbor's wider unseen one.
          {id: name + '-hit', type: 'line', source: f.main, ...(lineFilter(name) && {filter: lineFilter(name)}), layout: {'line-sort-key': ['get', 'dm_order']},
            paint: {'line-opacity': 0, 'line-width': ['max', ['get', 'dm_width'], HIT], 'line-offset': ['coalesce', ['get', 'dm_offset'], 0]}},
          {id: name, type: 'line', source: f.main, ...(lineFilter(name) && {filter: lineFilter(name)}), layout: {'line-sort-key': ['get', 'dm_order'], 'line-join': 'round'},
            paint: {'line-color': color, 'line-width': ['get', 'dm_width'], 'line-offset': ['coalesce', ['get', 'dm_offset'], 0],
              'line-opacity': ['coalesce', ['get', 'dm_opacity'], 1]}},
          {id: name + '-hover', type: 'line', source: f.main, filter: NONE,
            paint: {'line-color': t.text, 'line-width': 1, 'line-gap-width': ['get', 'dm_width'], 'line-offset': ['coalesce', ['get', 'dm_offset'], 0]}});
        part.hover.push([name, name + '-hover'], [name + '-hit', name + '-hover']);
      }
      if (nodes) {
        part.sources[f.nodes] = nodes;
        part.point.push(
          {id: name + '-nodes', type: 'circle', source: f.nodes, ...(shownKeys[name] && {filter: nodeFilter(name)}), layout: {'circle-sort-key': ['get', 'dm_order']},
            paint: {'circle-radius': ['coalesce', ['get', 'dm_r'], 3], 'circle-pitch-scale': 'viewport', 'circle-color': ink(t.node), ...ring(t, 1)}},
          {id: name + '-nodes-hover', type: 'circle', source: f.nodes, filter: NONE,
            paint: {'circle-radius': ['coalesce', ['get', 'dm_r'], 3], 'circle-pitch-scale': 'viewport', 'circle-opacity': 0, 'circle-stroke-color': t.text, 'circle-stroke-width': 1.5}});
        part.label.push({...labelLayer(name + '-labels', f.nodes, t), ...(shownKeys[name] && {filter: nodeFilter(name)})});
        part.hover.push([name + '-nodes', name + '-nodes-hover']);
      }
      if (arrows) {
        prepArrows(arrows, !deck);
        part.sources[f.arrows] = arrows;
        // Each head turns to a screen angle measured from projected points (screenArrows). A bearing is not a
        // screen angle under a non-conformal CRS, and MapLibre's map-aligned icons drift from local north on the
        // globe away from the view's center (11 to 88 degrees in a pixel test at 55 to 72 degrees out).
        part.arrow.push({id: name + '-arrows', type: 'symbol', source: f.arrows, ...(lineFilter(name) && {filter: lineFilter(name)}),
          layout: {'icon-image': 'dm-arrow', 'icon-size': ['get', 'dm_icon_size'], 'icon-anchor': 'top',
            'icon-offset': ['array', 'number', 2, ['get', 'dm_icon_offset']], 'icon-rotate': ['get', 'dm_screen'],
            'icon-rotation-alignment': 'viewport', 'icon-pitch-alignment': 'viewport',
            'icon-allow-overlap': true, 'icon-ignore-placement': true, 'symbol-sort-key': ['get', 'dm_order']},
          paint: {'icon-color': color, 'icon-halo-color': t.page, 'icon-halo-width': 1}});
      }
      return part;
    }
  };
}

function buildStyle(libs, t) {
  const proj = spec.projection, crs = proj.type === 'crs';
  // Arrows draw last, so no label covers a head. They stay out of label placement, so no node loses its name.
  const sources = {}, groups = {base: [], fill: [], line: [], point: [], edge: [], label: [], arrow: []};
  const hover = [];
  groups.base.push({id: 'dm-background', type: 'background', paint: {'background-color': crs ? t.page : t.ocean}});
  // Under a CRS, dm-spec.frame "none" leaves out the sphere, its ocean, and its graticule, so the land sits on the page.
  for (const s of ['frame', 'sphere', 'graticule'].filter(s => data[s] && !(crs && frameOf() === 'none'))) {
    sources[s] = {type: 'geojson', data: data[s]};
    groups.base.push({id: s + '-lines', type: 'line', source: s, filter: ['==', ['geometry-type'], 'LineString'],
      paint: {'line-color': t.graticule, 'line-width': 0.5}});
    // The sphere outline is the map's edge only under a CRS; on a globe or Mercator it would draw the
    // antimeridian and a ring around each pole.
    if (!crs) continue;
    groups.base.splice(-1, 0, {id: s + '-ocean', type: 'fill', source: s, filter: ['==', ['geometry-type'], 'Polygon'], paint: {'fill-color': t.ocean}});
    groups.edge.push({id: s + '-edge', type: 'line', source: s, filter: ['==', ['geometry-type'], 'Polygon'],
      paint: {'line-color': t['sphere-edge'], 'line-width': 0.75}});
  }
  const basemap = (spec.tiles || []).find(x => /\.pmtiles$/.test(x.url || ''));
  if (basemap && libs.basemaps) {
    sources.basemap = {type: 'vector', url: `pmtiles://${new URL(basemap.url, location.href).href}`,
      attribution: '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>'};
    const stack = fontStack();
    for (const layer of libs.basemaps.layers('basemap', libs.basemaps.namedFlavor(basemap.flavor || 'white'), {lang: spec.lang || 'en'})) {
      const {'icon-image': _, ...layout} = layer.layout || {};
      if (Array.isArray(layout['text-font'])) {
        // MapLibre reads weight and style from the first name, and a generic like system-ui can't carry them, so
        // a family no system has carries the style and the page's own stack draws the letters.
        const style = String(layout['text-font'][0]).match(/\b(Regular|Medium|Bold|Italic)\b/)?.[0] || 'Regular';
        layout['text-font'] = [`DataMap ${style}`, ...stack];
      }
      groups.base.push(Object.keys(layout).length ? {...layer, layout} : (({layout: _l, ...rest}) => rest)(layer));
    }
  }
  if (data.land) {
    sources.land = {type: 'geojson', data: data.land};
    groups.base.push({id: 'land', type: 'fill', source: 'land', paint: {'fill-color': t.land}},
      {id: 'land-edge', type: 'line', source: 'land', paint: {'line-color': t['land-edge'], 'line-width': 0.5}});
  }
  // Any data/base-<name>.geojson is quiet base information under the data: polygons pale with white edges, lines thin gray.
  for (const s of stems.filter(s => s.startsWith('base-'))) {
    sources[s] = {type: 'geojson', data: data[s]};
    groups.base.push({id: s + '-fill', type: 'fill', source: s, filter: POLYGONS, paint: {'fill-color': t.land}},
      {id: s + '-outline', type: 'line', source: s, filter: POLYGONS, paint: {'line-color': t['land-edge'], 'line-width': 0.5}},
      {id: s + '-line', type: 'line', source: s, filter: LINES, paint: {'line-color': t['base-line'], 'line-width': 0.6}});
  }
  const kinds = buildKinds(t, crs, !!libs.deck);
  for (const [name, L] of layersOf()) {
    const part = kinds[L.kind]?.(name, L) || {};
    for (const [id, fc] of Object.entries(part.sources || {})) sources[id] = {type: 'geojson', data: fc};
    for (const g of Object.keys(groups)) groups[g].push(...(part[g] || []));
    hover.push(...(part.hover || []));
  }
  const style = {version: 8, projection: crs ? {type: proj.name} : {type: proj.type}, sources,
    layers: Object.values(groups).flat()};
  return {style, hover, labels: groups.label.map(l => ({id: l.id, source: l.source}))};
}

async function registerCrs(maplibregl, proj4, source, p) {
  const projection = proj4('EPSG:4326', p.definition);
  // proj4 2.22.0 projects aea, laea, cea, stere, lcc, and tmerc to NaN everywhere when +x_0 and +y_0 are left out.
  const param = k => Number(p.definition.match(new RegExp(`\\+${k}=(-?[\\d.]+)`))?.[1] ?? 0);
  const center = [param('lon_0'), param('lat_0')];
  let at;
  try { at = projection.forward(center); } catch { at = [NaN, NaN]; }
  if (!at.every(Number.isFinite)) {
    throw new Error(`the CRS ${p.name} projects its own center (${center.join(', ')}) to ${at.join(', ')}, so nothing can draw: ` +
      `"${p.definition}"; add +x_0=0 +y_0=0 to the definition, as datamap.py crs prints it`);
  }
  // proj4's UMD build defines self.proj4 in a worker as in the page. A blob URL made on a file:// page is
  // blob:null/..., which the workers can't import; a data URL works from any origin.
  const handler = `${source}\nself.setProjectionHandler(definition => self.proj4(definition));\n`;
  await maplibregl.importScriptInWorkers(`data:text/javascript;charset=utf-8,${encodeURIComponent(handler)}`);
  let half = 0;
  for (let lon = -180; lon <= 180; lon += 2) for (let lat = -90; lat <= 90; lat += 2) {
    try {
      const [x, y] = projection.forward([lon, lat]);
      if (Number.isFinite(x) && Number.isFinite(y)) half = Math.max(half, Math.abs(x), Math.abs(y));
    } catch { /* outside the projection's domain */ }
  }
  half *= 1.04;
  maplibregl.addProjection({name: p.name, definition: p.definition, projection,
    tileMatrixSet: {origin: [-half, half], extentAtZoom0: 2 * half}});
}

// ---------- the view: fitted to the data, with zoom and panning bounded by it ----------

const frameOf = () => spec.frame ?? FRAME;

// A world under a CRS runs from just inside the cut at lon_0 - 180 to just inside it at lon_0 + 180: geo --lon0 moves
// the pieces west of the cut 360 degrees east, so a -180..180 box would crop both sides of a map centered off 0.
function worldLons() {
  const lon0 = spec.projection.type === 'crs' ? Number(spec.projection.definition?.match(/\+lon_0=(-?[\d.]+)/)?.[1] ?? 0) : 0;
  return [lon0 - 180 + 1e-5, lon0 + 180 - 1e-5];
}

// What the view fits: a named world, a [W, S, E, N] box, or the data's bounds. A world under a CRS with no frame
// runs the full width but only the latitudes its data covers, so no band of empty ocean sits below the southernmost
// country when Antarctica is left off.
function fitBox(pts) {
  const e = spec.extent;
  if (e === 'world') {
    const [w, east] = worldLons();
    if (spec.projection.type !== 'crs' || frameOf() !== 'none' || !pts.length) return [[w, -90], [east, 90]];
    const ys = pts.map(p => p[1]);
    return [[w, ys.reduce((a, b) => Math.min(a, b))], [east, ys.reduce((a, b) => Math.max(a, b))]];
  }
  if (Array.isArray(e)) return [[e[0], e[1]], [e[2], e[3]]];
  return bbox(pts.length ? pts : [[-180, -90], [180, 90]]);
}

// Points along a [[W, S], [E, N]] box's four edges, which a CRS bends into the map's outline.
function boxEdge([[w, south], [e, north]]) {
  const pts = [];
  for (let i = 0; i <= 72; i++) {
    const t = i / 72, lon = w + t * (e - w), lat = south + t * (north - south);
    pts.push([lon, south], [lon, north], [w, lat], [e, lat]);
  }
  return pts;
}

// How far, in px, the world's edge runs past the map's frame under a CRS: 0 when the whole outline is in view.
function edgeCut(map) {
  if (spec.extent !== 'world' || spec.projection.type !== 'crs') return null;
  const {clientWidth: W, clientHeight: H} = map.getCanvas();
  return Math.round(10 * Math.max(0, ...boxEdge(fitBox(thematicPoints())).map(c => {
    const p = map.project(c);
    return Math.max(-p.x, p.x - W, -p.y, p.y - H);
  }))) / 10;
}

function walk(c, out) {
  if (typeof c[0] === 'number') out.push(c);
  else for (const x of c) walk(x, out);
}
function thematicPoints() {
  const pts = [];
  for (const [name, L] of layersOf()) {
    const f = filesOf(name, L);
    for (const s of new Set([f.main, f.nodes])) for (const feat of data[s]?.features || []) if (feat.geometry) walk(feat.geometry.coordinates, pts);
  }
  return pts;
}
function meanCenter(pts) {
  if (!pts.length) return [0, 20];
  let x = 0, y = 0, z = 0;
  for (const [lon, lat] of pts) {
    x += Math.cos(lat * RAD) * Math.cos(lon * RAD); y += Math.cos(lat * RAD) * Math.sin(lon * RAD); z += Math.sin(lat * RAD);
  }
  return [Math.atan2(y, x) / RAD, Math.atan2(z, Math.hypot(x, y)) / RAD];
}
// The globe opens on the center, on a 5-degree grid no more than 45 degrees from the equator, that keeps the most
// inflow within 64 degrees of the middle, where the disk still reads, and on a tie the one that brings it nearest the
// middle. A mean position can leave the largest destinations on the far side, and a center near a pole turns the
// continents on their sides.
function globeCenter(pts) {
  const inflow = new Map();
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows') continue;
    const f = filesOf(name, L);
    const at = Object.fromEntries((data[f.nodes]?.features || []).map(n => [n.properties.dm_key ?? n.id, n.geometry.coordinates]));
    for (const {properties: p} of data[f.main]?.features || []) {
      if (at[p.dm_d]) inflow.set(p.dm_d, {at: at[p.dm_d], v: (inflow.get(p.dm_d)?.v || 0) + (p.dm_value || 0)});
    }
  }
  if (!inflow.size) return meanCenter(pts);
  let best = null;
  for (let lat = -45; lat <= 45; lat += 5) for (let lon = -180; lon < 180; lon += 5) {
    let seen = 0, near = 0;
    for (const {at, v} of inflow.values()) {
      const deg = angularKm(at, [lon, lat]) / EARTH_KM / RAD;
      if (deg <= 64) seen += v;
      near += v * Math.max(0, Math.cos(deg * RAD));
    }
    if (!best || seen > best.seen || (seen === best.seen && near > best.near)) best = {c: [lon, lat], seen, near};
  }
  return best.c;
}
function bbox(pts) {
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  return [[Math.min(...xs), Math.min(...ys)], [Math.max(...xs), Math.max(...ys)]];
}
function destination([lon, lat], bearing, deg) {
  const p1 = lat * RAD, l1 = lon * RAD, b = bearing * RAD, d = deg * RAD;
  const p2 = Math.asin(Math.sin(p1) * Math.cos(d) + Math.cos(p1) * Math.sin(d) * Math.cos(b));
  const l2 = l1 + Math.atan2(Math.sin(b) * Math.sin(d) * Math.cos(p1), Math.cos(d) - Math.sin(p1) * Math.sin(p2));
  return [((l2 / RAD + 540) % 360) - 180, p2 / RAD];
}
function globeRadius(map, center) {
  const c = map.project(center);
  const r = [0, 90, 180, 270].map(b => { const p = map.project(destination(center, b, 80)); return Math.hypot(p.x - c.x, p.y - c.y); });
  return Math.max(...r) / Math.sin(80 * RAD);
}
// MapLibre keeps the globe one size as its center moves by adding log2 of the ratio of the latitudes' cosines to the
// zoom, but it holds the zoom to maxZoom as it stands, so limits set at the fitted latitude let the reader shrink
// the globe, or stop zooming in, once it turns toward the equator. Its minZoom also binds between the two steps of
// a jumpTo or easeTo, which adds the latitude's change twice. So on a globe the camera hook holds the zoom between
// the fitted zoom at the center's latitude plus the dm-spec offsets, and MapLibre's own limits stay out of the way.
let zoomBand = null;
const fittedAt = (band, lat) => band.z0 + Math.log2(Math.cos(Math.min(Math.abs(lat), 85) * RAD) / Math.cos(band.lat0 * RAD));
function zoomLimits(map) {
  if (!zoomBand) return [map.getMinZoom(), map.getMaxZoom()];
  const z = fittedAt(zoomBand, map.getCenter().lat);
  return [zoomBand.lo == null ? map.getMinZoom() : z + zoomBand.lo, zoomBand.hi == null ? map.getMaxZoom() : z + zoomBand.hi];
}

// The globe's radius in px, read as its scale at the view's center, where the surface faces the camera: unlike the
// disk's outline, this holds at any zoom.
function globeScale(map) {
  const c = map.getCenter().toArray(), o = map.project(c), p = map.project(destination(c, 90, 0.5));
  return Math.hypot(p.x - o.x, p.y - o.y) / Math.sin(0.5 * RAD);
}

// The view's margin: 14 px past the data, and past its largest circle.
const fitPad = () => 14 + Math.max(0, ...layersOf().flatMap(([name, L]) => [name, filesOf(name, L).nodes])
  .flatMap(s => (data[s]?.features || []).map(f => f.properties?.dm_r || 0)));

function fitView(map) {
  const type = spec.projection.type, pts = thematicPoints(), pad = fitPad();
  const {clientWidth: w, clientHeight: h} = map.getContainer();
  map.setTransformCameraUpdate(null);
  zoomBand = null;
  map.setMinZoom(null);
  map.setMaxZoom(null);
  map.setMaxBounds(null);
  let fitted;
  if (type === 'globe') {
    const center = Array.isArray(spec.center) ? spec.center : globeCenter(pts);
    map.jumpTo({center, zoom: 1.5});
    for (let i = 0; i < 3; i++) map.setZoom(map.getZoom() + Math.log2((Math.min(w, h) / 2 - pad) / globeRadius(map, center)));
  } else {
    const b = fitBox(pts);
    map.fitBounds(b, {padding: pad, animate: false});
    fitted = b;
  }
  const z0 = map.getZoom();
  const zoomOf = v => typeof v === 'number' ? v : typeof v === 'string' && /^fit([+-]\d+(\.\d+)?)?$/.test(v) ? z0 + Number(v.slice(3) || 0) : null;
  const zmin = zoomOf(spec.zoom?.min), zmax = zoomOf(spec.zoom?.max);
  if (type === 'globe' && (zmin != null || zmax != null)) {
    const band = zoomBand = {z0, lat0: map.getCenter().lat, lo: zmin == null ? null : zmin - z0, hi: zmax == null ? null : zmax - z0};
    map.setMinZoom(-2);
    if (band.hi != null) map.setMaxZoom(Math.min(24, fittedAt(band, 0) + band.hi));
    map.setTransformCameraUpdate(tr => {
      const z = fittedAt(band, tr.center.lat);
      const zoom = Math.min(Math.max(tr.zoom, band.lo == null ? -2 : z + band.lo), band.hi == null ? 24 : z + band.hi);
      return zoom === tr.zoom ? {} : {zoom};
    });
  } else {
    if (zmin != null) map.setMinZoom(zmin);
    if (zmax != null) map.setMaxZoom(zmax);
  }
  if (fitted && spec.extent !== 'world') {
    // Panning stops about 4 degrees of longitude and 3 of latitude past the data (Muehlenhaus ch. 9).
    const v = map.getBounds();
    map.setMaxBounds([[Math.min(fitted[0][0] - 4, v.getWest()), Math.max(Math.min(fitted[0][1] - 3, v.getSouth()), -90)],
      [Math.max(fitted[1][0] + 4, v.getEast()), Math.min(Math.max(fitted[1][1] + 3, v.getNorth()), 90)]]);
  }
}

function screenArrows(map) {
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows') continue;
    const stem = filesOf(name, L).arrows, fc = data[stem];
    if (!fc) continue;
    for (const f of fc.features) {
      const at = f.geometry.coordinates, p = map.project(at), q = map.project(destination(at, f.properties.dm_bearing, 0.05));
      f.properties.dm_screen = Math.atan2(q.x - p.x, p.y - q.y) / RAD;
    }
    map.getSource(stem).setData(fc);
  }
}

// ---------- interaction: a tooltip from dm_tip, and an outline on the feature under the pointer ----------

// One feature answers the pointer: the topmost of the hover layers' features under it, outlined alone.
function interact(map, hover) {
  const tip = html('div', {class: 'dm-tip'}, $('dm-map-cell'));
  const show = (text, x, y) => {
    if (!text) { tip.style.display = 'none'; return; }
    tip.textContent = text;
    tip.style.display = 'block';
    const cell = $('dm-map-cell'), right = x + 14 + tip.offsetWidth > cell.clientWidth;
    tip.style.left = `${right ? x - 14 - tip.offsetWidth : x + 14}px`;
    tip.style.top = `${Math.max(y - tip.offsetHeight - 8, 0)}px`;
  };
  const outlines = new Map(hover);
  let lit = null;
  const light = (outline, filter) => {
    if (lit && lit !== outline) map.setFilter(lit, NONE);
    if (outline) map.setFilter(outline, filter);
    lit = outline;
  };
  const answer = e => {
    const layers = [...outlines.keys()].filter(id => map.getLayer(id));
    const f = layers.length ? map.queryRenderedFeatures(e.point, {layers})[0] : null;
    if (!f) { light(null); map.getCanvas().style.cursor = ''; show(null); return; }
    light(outlines.get(f.layer.id), f.properties.dm_key != null ? ['==', ['get', 'dm_key'], f.properties.dm_key] : ['==', ['id'], f.id ?? '__dm_none__']);
    map.getCanvas().style.cursor = focusLayer && f.layer.id === focusLayer + '-nodes' ? 'pointer' : 'default';
    show(f.properties.dm_tip || f.properties.dm_label, e.point.x, e.point.y);
  };
  // A tap fires click, not mousemove, so the tooltip answers both.
  for (const kind of ['mousemove', 'click']) map.on(kind, answer);
  map.getCanvas().addEventListener('mouseleave', () => { light(null); show(null); });
  return show;
}

// A globe on a phone fills most of the screen, so a one-finger swipe that starts vertical scrolls the page and one
// that starts sideways turns the globe; two fingers still zoom. The canvas leaves vertical panning to the browser,
// and MapLibre never sees the moves of a vertical swipe, nor the first few px of any swipe, while its way is unknown.
function swipeScrolls(map) {
  if (spec.projection.type !== 'globe') return;
  for (const e of [map.getCanvasContainer(), map.getCanvas()]) e.style.touchAction = 'pan-y';
  let start = null, vertical = null;
  const cell = $('dm-map-cell'), opts = {capture: true, passive: true};
  cell.addEventListener('touchstart', e => {
    start = e.touches.length === 1 ? [e.touches[0].clientX, e.touches[0].clientY] : null;
    vertical = null;
  }, opts);
  cell.addEventListener('touchmove', e => {
    if (!start || e.touches.length !== 1) return;
    if (vertical === null) {
      const dx = e.touches[0].clientX - start[0], dy = e.touches[0].clientY - start[1];
      if (Math.hypot(dx, dy) >= 6) vertical = Math.abs(dy) > Math.abs(dx);
    }
    if (vertical !== false) e.stopPropagation();
  }, opts);
}

// ---------- deck.gl arcs: great circles raised by a height tied to length alone ----------

function arcLayers(deck, t, show) {
  const out = [];
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows') continue;
    const f = filesOf(name, L), nodes = data[f.nodes]?.features || [];
    const at = Object.fromEntries(nodes.map(n => [n.properties.dm_key ?? n.id, n.geometry.coordinates]));
    const arcs = (data[f.main]?.features || []).map(l => l.properties).filter(p => at[p.dm_o] && at[p.dm_d] && drawnFlow(name, p))
      .map(p => ({...p, from: at[p.dm_o], to: at[p.dm_d]})).sort((a, b) => a.dm_order - b.dm_order);
    if (!arcs.length) continue;
    const longest = Math.max(...arcs.map(a => a.dm_km || 1));
    const apex = spec.arcs?.apex ?? ARC_APEX;
    // deck.gl's arc peaks at height * length / 2 (arc-layer-vertex.glsl), so this puts the longest flow's apex at
    // APEX of the Earth's radius and every other apex in proportion to its length.
    const height = 2 * apex / (longest / EARTH_KM);
    const arcColor = a => focused?.layer === name ? (a.dm_o === focused.key ? tok('out') : tok('in')) : a.dm_fill || L.color || t.flow;
    out.push({name, apex, longest, height, layer: new deck.ArcLayer({
      id: name, data: arcs, greatCircle: true, numSegments: 64,
      // The globe culls back faces and 9.4.1's arc strips wind clockwise, so without this they vanish (deck.gl #10670).
      parameters: {cullMode: 'none'},
      // Where the maplibre page draws its lines: under the nodes, their names, and the arrowheads.
      beforeId: data[f.nodes] ? name + '-nodes' : data[f.arrows] ? name + '-arrows' : undefined,
      getSourcePosition: a => a.from, getTargetPosition: a => a.to, getHeight: height,
      getWidth: a => a.dm_width, widthUnits: 'pixels',
      getSourceColor: a => [...rgb(arcColor(a)), 255 * (a.dm_opacity ?? 1)],
      getTargetColor: a => [...rgb(arcColor(a)), 255 * (a.dm_opacity ?? 1)],
      pickable: true, onHover: info => show(info.object?.dm_tip, info.x, info.y), onClick: info => show(info.object?.dm_tip, info.x, info.y)
    })});
  }
  return out;
}

// ---------- point labels: each name in the corner its flows, arrowheads, and neighbors leave clearest ----------

// Every name of every label layer, and what it must stay clear of, in screen px at the current view. Flows are
// segments with their half-widths, deck.gl arcs too as the reader sees them raised, each arrowhead is its triangle
// and a short wide segment along its line, and nodes and symbols are circles.
function labelScene(map, labels, deck) {
  const xy = c => { const p = map.project(c); return [p.x, p.y]; };
  const center = map.getCenter().toArray(), horizon = spec.projection.type === 'globe' ? horizonDeg(map) : Infinity;
  const front = c => angularKm(c, center) / EARTH_KM / RAD < horizon;
  const {clientWidth: W, clientHeight: H} = map.getCanvas();
  const size = parseFloat(tok('t4'));
  const segs = [], heads = [], circles = [];
  for (const [name, L] of layersOf()) {
    const f = filesOf(name, L);
    const points = data[L.kind === 'flows' ? f.nodes : name]?.features || [];
    for (const n of L.kind === 'classes' ? [] : points) {
      if (front(n.geometry.coordinates) && !nodeHidden(f.nodes, n)) circles.push({key: `${L.kind === 'flows' ? f.nodes : name}:${n.properties.dm_lid}`,
        c: xy(n.geometry.coordinates), r: n.properties.dm_r || 3, name: n.properties.dm_label ?? null});
    }
    if (L.kind !== 'flows') continue;
    const names = Object.fromEntries(points.map(n => [n.properties.dm_key ?? n.id, n.properties.dm_label ?? n.id]));
    if (deck) segs.push(...arcSegs(map, name, front));
    for (const line of deck ? [] : data[f.main]?.features || []) {
      if (!drawnFlow(name, line.properties)) continue;
      const g = line.geometry, hw = (line.properties.dm_width || 1) / 2;
      for (const part of g.type === 'MultiLineString' ? g.coordinates : [g.coordinates]) {
        for (let i = 1; i < part.length; i++) {
          if (front(part[i - 1]) && front(part[i])) segs.push({a: xy(part[i - 1]), b: xy(part[i]), hw, weight: 1});
        }
      }
    }
    for (const a of data[f.arrows]?.features || []) {
      const at = a.geometry.coordinates, q = a.properties;
      if (!front(at) || !drawnFlow(name, q)) continue;
      // The head draws turned to dm_screen with its tip dm_setback + 1 px back from the node (prepArrows).
      const p = xy(at), turn = (q.dm_screen ?? q.dm_bearing ?? 0) * RAD, u = [-Math.sin(turn), Math.cos(turn)];
      const len = q.dm_arrow || 8, half = len * ARROW.base / ARROW.len / 2, back = (q.dm_setback || 0) + 1;
      const side = (q.dm_icon_offset?.[0] ?? 0) * (q.dm_icon_size ?? 1);
      const tip = [p[0] + u[0] * back + u[1] * side, p[1] + u[1] * back - u[0] * side], base = [tip[0] + u[0] * len, tip[1] + u[1] * len];
      heads.push({flow: `${names[q.dm_o] ?? q.dm_o} to ${names[q.dm_d] ?? q.dm_d}`,
        tri: [tip, [base[0] - u[1] * half, base[1] + u[0] * half], [base[0] + u[1] * half, base[1] - u[0] * half]]});
      segs.push({a: tip, b: base, hw: len * 0.3, weight: 3});
    }
  }
  const rows = f => String(f.properties.dm_text ?? f.properties.dm_label).split('\n');
  const items = labels.flatMap(({id, source}, layer) => (data[source]?.features || []).filter(f => f.properties.dm_label != null && !nodeHidden(source, f))
    .map(f => {
      const c = f.geometry.coordinates, p = xy(c);
      return {layer: id, rank: layer, lid: f.properties.dm_lid, key: `${source}:${f.properties.dm_lid}`, text: String(f.properties.dm_label),
        order: f.properties.dm_order ?? 0, p, r: f.properties.dm_r || 3, front: front(c),
        w: Math.max(...rows(f).map(r => measure(r, highlighted.has(keyOf(f))))), lines: rows(f).length,
        seen: front(c) && p[0] >= 0 && p[1] >= 0 && p[0] <= W && p[1] <= H};
    }))
    // Larger names first, as symbol-sort-key places them (Slocum §12.5.1).
    .sort((a, b) => a.rank - b.rank || a.order - b.order);
  return {items, segs, heads, circles, W, H, size};
}

// Each drawn deck.gl arc as screen segments. deck.gl lifts a great-circle arc sqrt(t(1 - t)) * length * height above
// the ground (arc-layer-vertex.glsl), so the longest flow's apex sits at dm-spec.arcs.apex of the Earth's radius; on
// the globe, whose camera is nearly orthographic, a point that high lies (1 + lift) times as far from the globe's
// center on screen as the ground under it, and shows unless the globe hides it.
function arcSegs(map, name, front) {
  const arc = (live.arcs || []).find(a => a.name === name);
  if (!arc) return [];
  const globe = spec.projection.type === 'globe', c = map.project(map.getCenter()), out = [];
  const center = map.getCenter().toArray();
  for (const a of arc.layer.props.data) {
    const deg = angularKm(a.from, a.to) / EARTH_KM / RAD, b = bearingTo(a.from, a.to), share = (a.dm_km || 0) / (arc.longest || 1);
    let last = null;
    for (let i = 0; i <= 24; i++) {
      const s = i / 24, at = destination(a.from, b, deg * s), g = map.project(at);
      const lift = globe ? 2 * arc.apex * share * Math.sqrt(s * (1 - s)) : 0;
      const p = [c.x + (g.x - c.x) * (1 + lift), c.y + (g.y - c.y) * (1 + lift)];
      const away = angularKm(at, center) / EARTH_KM;
      const seen = front(at) || (globe && (1 + lift) * Math.sin(Math.min(away, Math.PI / 2)) > 1);
      if (seen && last) out.push({a: last, b: p, hw: (a.dm_width || 1) / 2, weight: 1});
      last = seen ? p : null;
    }
  }
  return out;
}

// How far from the view's center the globe's horizon lies, in degrees. Past it a projected point turns back toward
// the center, so the farthest one marks it; MapLibre draws nothing past it.
function horizonDeg(map) {
  const c = map.getCenter().toArray(), o = map.project(c);
  let at = 90, far = -1;
  for (let d = 30; d <= 120; d += 0.5) {
    const p = map.project(destination(c, 90, d)), r = Math.hypot(p.x - o.x, p.y - o.y);
    if (r > far) { far = r; at = d; }
  }
  return at;
}

// Each corner in Slocum's order at the node's edge, then again about twice as far out for a name its flows crowd.
function labelOptions(item, size) {
  const off = 0.25 + item.r / size;
  return [1, 1.9].flatMap((reach, ring) => CORNERS.map(([anchor, sx, sy], corner) => {
    const d = (sx && sy ? off / Math.SQRT2 : off) * reach;
    return {id: ring * CORNERS.length + corner, ring, anchor, sx, sy, offset: [sx * d, sy * d].map(v => Math.round(v * 1000) / 1000)};
  }));
}
// The name's box for an anchor's direction (sx, sy) and an offset in ems.
function labelBox(item, {sx, sy, offset}, size, inset = 0) {
  const h = size * 1.2 * (item.lines || 1);
  const cx = item.p[0] + offset[0] * size + sx * item.w / 2, cy = item.p[1] + offset[1] * size + sy * h / 2;
  return [cx - item.w / 2, cy - h / 2 + inset, cx + item.w / 2, cy + h / 2 - inset];
}
// How a label layer draws each name, read back from its style: a constant, or a match on dm_lid with literal
// outputs, as placeLabels writes them. A variable anchor counts as its first choice.
function drawnLayout(map, id, size) {
  const get = k => map.getLayoutProperty(id, k);
  const plain = v => Array.isArray(v) && v[0] === 'literal' ? v[1] : v;
  const byLid = v => {
    if (!(Array.isArray(v) && v[0] === 'match')) return () => plain(v);
    const out = new Map();
    for (let i = 2; i < v.length - 1; i += 2) out.set(v[i], plain(v[i + 1]));
    return lid => out.has(lid) ? out.get(lid) : plain(v.at(-1));
  };
  const anchor = get('text-variable-anchor') ? () => get('text-variable-anchor')[0] : byLid(get('text-anchor') ?? 'center');
  const offset = byLid(get('text-offset') ?? [0, 0]), radial = get('text-radial-offset');
  return item => {
    const [, sx, sy] = CORNERS.find(c => c[0] === anchor(item.lid)) ?? ['center', 0, 0];
    if (radial == null) return {sx, sy, offset: offset(item.lid)};
    const d = (typeof radial === 'number' ? radial : 0.25 + item.r / size) / (sx && sy ? Math.SQRT2 : 1);
    return {sx, sy, offset: [sx * d, sy * d]};
  };
}
// The length of a segment inside a box grown by the segment's half-width (Liang-Barsky).
function clippedLength({a, b, hw}, [x0, y0, x1, y1]) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  let t0 = 0, t1 = 1;
  for (const [p, q] of [[-dx, a[0] - x0 + hw], [dx, x1 + hw - a[0]], [-dy, a[1] - y0 + hw], [dy, y1 + hw - a[1]]]) {
    if (p === 0) { if (q < 0) return 0; continue; }
    const r = q / p;
    if (p < 0) { if (r > t1) return 0; t0 = Math.max(t0, r); } else { if (r < t0) return 0; t1 = Math.min(t1, r); }
  }
  return (t1 - t0) * Math.hypot(dx, dy);
}
const boxesMeet = (p, q, pad) => p[0] < q[2] + pad && q[0] < p[2] + pad && p[1] < q[3] + pad && q[1] < p[3] + pad;
function circleMeetsBox({c, r}, [x0, y0, x1, y1], pad) {
  return Math.hypot(c[0] - Math.min(Math.max(c[0], x0), x1), c[1] - Math.min(Math.max(c[1], y0), y1)) < r + pad;
}
// Separating axes: the box's two and the triangle's three edge normals.
function triangleMeetsBox(tri, [x0, y0, x1, y1]) {
  const corners = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
  const axes = [[1, 0], [0, 1], ...tri.map((a, i) => { const b = tri[(i + 1) % 3]; return [a[1] - b[1], b[0] - a[0]]; })];
  return axes.every(n => {
    const t = tri.map(p => p[0] * n[0] + p[1] * n[1]), r = corners.map(p => p[0] * n[0] + p[1] * n[1]);
    return Math.max(...t) > Math.min(...r) && Math.max(...r) > Math.min(...t);
  });
}
// What a box laid over the map covers: the length of flow under it, each arrowhead and circle it touches but OWN,
// and a heavy cost for leaving the frame.
function boxCost(box, scene, own) {
  let cost = 0;
  for (const s of scene.segs) cost += s.weight * clippedLength(s, box) / 1.5;
  for (const hd of scene.heads) if (triangleMeetsBox(hd.tri, box)) cost += 150;
  for (const k of scene.circles) if (k.key !== own && circleMeetsBox(k, box, 1)) cost += 200;
  if (box[0] < 0 || box[1] < 0 || box[2] > scene.W || box[3] > scene.H) cost += 1000;
  return cost;
}
// A name farther from its point costs a little, so the outer ring wins only where it clears a line. A name that sits
// nearer another circle than its own reads as that circle's name (Slocum §12.5.2), so that costs nearly as much as
// covering the circle.
function labelCost(item, o, scene) {
  const box = labelBox(item, o, scene.size);
  const gap = (c, r) => Math.hypot(c[0] - Math.min(Math.max(c[0], box[0]), box[2]), c[1] - Math.min(Math.max(c[1], box[1]), box[3])) - r;
  const own = gap(item.p, item.r);
  const nearer = scene.circles.filter(k => k.key !== item.key && gap(k.c, k.r) < own + 2).length;
  return o.ring * 4 + boxCost(box, scene, item.key) + 150 * nearer;
}
function shownLabels(map, labels) {
  const out = new Set();
  for (const {id, source} of labels) for (const f of map.queryRenderedFeatures({layers: [id]})) out.add(`${source}:${f.properties.dm_lid}`);
  return out;
}

let labelPlan = null;

// One corner per name, through per-feature text-anchor and a text-offset match on dm_lid with literal outputs;
// maplibre-gl 6.18 accepts a per-feature text-variable-anchor-offset and silently ignores it. No fixed margin
// between name boxes matches MapLibre's collision test, so MapLibre has the last word: a name it hides loses that
// corner, and the pass runs again.
async function placeLabels(map, labels, deck) {
  if (!labels.length) return;
  labelPlan = {labels, deck};
  const scene = labelScene(map, labels, deck);
  for (const item of scene.items) item.options = labelOptions(item, scene.size).map(o => ({...o, cost: labelCost(item, o, scene)}));
  const refused = new Map();
  for (let pass = 0; pass < 8; pass++) {
    const taken = [];
    for (const item of scene.items) {
      const no = refused.get(item.key);
      let best = null, low = Infinity;
      for (const o of item.options) {
        const box = labelBox(item, o, scene.size);
        const score = o.cost + (no?.has(o.id) ? 1e6 : 0) + 500 * taken.filter(b => boxesMeet(box, b, 3)).length;
        if (score < low) { best = o; low = score; }
      }
      item.chosen = best;
      if (item.seen) taken.push(labelBox(item, best, scene.size));
    }
    for (const {id} of labels) {
      const mine = scene.items.filter(i => i.layer === id);
      if (!mine.length) continue;
      map.setLayoutProperty(id, 'text-radial-offset', undefined);
      map.setLayoutProperty(id, 'text-anchor', ['match', ['get', 'dm_lid'], ...mine.flatMap(i => [i.lid, i.chosen.anchor]), 'bottom-left']);
      map.setLayoutProperty(id, 'text-offset', ['match', ['get', 'dm_lid'], ...mine.flatMap(i => [i.lid, ['literal', i.chosen.offset]]),
        ['literal', [0, 0]]]);
    }
    map.triggerRepaint();
    await once(map, 'idle');
    const shown = shownLabels(map, labels);
    const hidden = scene.items.filter(i => i.seen && !shown.has(i.key));
    if (!hidden.length) return;
    for (const i of hidden) refused.set(i.key, new Set([...(refused.get(i.key) || []), i.chosen.id]));
  }
}

// Per label layer: the names in view, the ones MapLibre drew, each arrowhead over a drawn name's letters, and the
// names out of view, on a globe's far side or past the frame.
function labelReport(map) {
  if (!map || !labelPlan) return [];
  const {labels, deck} = labelPlan;
  const scene = labelScene(map, labels, deck), shown = shownLabels(map, labels);
  return labels.map(({id}) => {
    const mine = scene.items.filter(i => i.layer === id && i.seen), drawn = mine.filter(i => shown.has(i.key));
    const layout = drawnLayout(map, id, scene.size);
    const covered = drawn.flatMap(i => {
      // The letters and their halo fill about the middle 1 em of the 1.2 em line box.
      const box = labelBox(i, layout(i), scene.size, scene.size * 0.1);
      return scene.heads.filter(hd => triangleMeetsBox(hd.tri, box)).map(hd => ({name: i.text, arrow: hd.flow}));
    });
    const unseen = scene.items.filter(i => i.layer === id && !i.seen).map(i => ({name: i.text, far: !i.front}));
    // A drawn name nearer another circle than its own, which a reader takes for that circle's name, and a name
    // that runs past the map's edge.
    const nearer = drawn.flatMap(i => {
      const box = labelBox(i, layout(i), scene.size);
      const gap = (c, r) => Math.hypot(c[0] - Math.min(Math.max(c[0], box[0]), box[2]), c[1] - Math.min(Math.max(c[1], box[1]), box[3])) - r;
      const own = gap(i.p, i.r), other = scene.circles.filter(k => k.key !== i.key).sort((a, b) => gap(a.c, a.r) - gap(b.c, b.r))[0];
      return other && gap(other.c, other.r) < own - 1 ? [{name: i.text, circle: other.name ?? '?'}] : [];
    });
    const cut = drawn.filter(i => {
      const [x0, y0, x1, y1] = labelBox(i, layout(i), scene.size, scene.size * 0.1);
      return x0 < -1 || y0 < -1 || x1 > scene.W + 1 || y1 > scene.H + 1;
    }).map(i => i.text);
    return {layer: id, nodes: mine.length, rendered: drawn.map(i => i.text), hidden: mine.filter(i => !shown.has(i.key)).map(i => i.text), covered, unseen, nearer, cut};
  });
}

// ---------- annotations: the finding written on the map, a quiet note with a short leader to its place ----------

// A note wraps at one of NOTE.widths px and sits at one of six leader lengths in each of Slocum's label corners,
// whichever covers least of the flows and arcs, arrowheads, circles, names, other notes, and land: a note over land
// reads as a place there, so it costs more than a long leader out to sea or off the globe. A place with no node gets
// a dot.
const NOTE = {widths: [180, 120], reaches: [12, 24, 40, 64, 100, 140], dot: 2, area: 320};
let notes = [];

function resolveNotes() {
  const nodes = {};
  for (const [name, L] of layersOf()) {
    const stem = L.kind === 'flows' ? filesOf(name, L).nodes : L.kind === 'sizes' ? name : null;
    for (const f of (stem && data[stem]?.features) || []) nodes[String(f.properties.dm_key ?? f.id)] = {f, key: `${stem}:${f.properties.dm_lid}`};
  }
  notes = (spec.annotations || []).map(a => {
    const key = typeof a.at === 'string' ? a.at.match(/^node:(.+)$/)?.[1] : null, hit = key == null ? null : nodes[key];
    const at = hit ? hit.f.geometry.coordinates : Array.isArray(a.at) && a.at.length === 2 && a.at.every(Number.isFinite) ? a.at : null;
    return {text: String(a.text ?? ''), at, node: hit?.f.properties.dm_label ?? null, circle: hit?.key ?? null,
      r: hit ? hit.f.properties.dm_r || 3 : NOTE.dot, why: at ? null : key != null ? `no node has the key ${key}` : '"at" is neither [lon, lat] nor "node:<key>"'};
  });
}

function bearingTo([lon1, lat1], [lon2, lat2]) {
  const p1 = lat1 * RAD, p2 = lat2 * RAD, dl = (lon2 - lon1) * RAD;
  return Math.atan2(Math.sin(dl) * Math.cos(p2), Math.cos(p1) * Math.sin(p2) - Math.sin(p1) * Math.cos(p2) * Math.cos(dl)) / RAD;
}

// Where a note's leader starts: its place, or on a globe whose far side holds the place, the rim in the place's
// direction (the farthest point the globe draws along that bearing), pulled inside the frame when zoomed in.
function noteAnchor(map, n) {
  const {clientWidth: W, clientHeight: H} = map.getCanvas();
  const xy = c => { const p = map.project(c); return [p.x, p.y]; };
  const inside = ([x, y]) => x >= 0 && y >= 0 && x <= W && y <= H;
  const near = p => inside(p) ? {p, r: n.r, far: false} : null;
  if (spec.projection.type !== 'globe') return near(xy(n.at));
  const c = map.getCenter().toArray();
  if (angularKm(n.at, c) / EARTH_KM / RAD < horizonDeg(map)) return near(xy(n.at));
  const o = xy(c), b = bearingTo(c, n.at);
  let rim = o, far = -1;
  for (let d = 30; d <= 120; d += 0.5) {
    const p = xy(destination(c, b, d)), r = Math.hypot(p[0] - o[0], p[1] - o[1]);
    if (r > far) { far = r; rim = p; }
  }
  const pad = 4, dx = rim[0] - o[0], dy = rim[1] - o[1];
  const t = Math.min(1, ...[[dx, o[0], W], [dy, o[1], H]].map(([v, at, max]) => v > 0 ? (max - pad - at) / v : v < 0 ? (pad - at) / v : 1));
  return {p: [o[0] + dx * t, o[1] + dy * t], r: NOTE.dot, far: true};
}

// The boxes of the names MapLibre drew, where each one's layout puts it.
function drawnNames(map, scene) {
  if (!labelPlan) return [];
  const shown = shownLabels(map, labelPlan.labels);
  return labelPlan.labels.flatMap(({id}) => {
    const layout = drawnLayout(map, id, scene.size);
    return scene.items.filter(i => i.layer === id && i.seen && shown.has(i.key)).map(i => ({text: i.text, box: labelBox(i, layout(i), scene.size)}));
  });
}

function segMeetsCircle({a, b}, {c, r}) {
  const dx = b[0] - a[0], dy = b[1] - a[1], t = Math.max(0, Math.min(1, ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / (dx * dx + dy * dy || 1)));
  return Math.hypot(a[0] + t * dx - c[0], a[1] + t * dy - c[1]) < r;
}

// Turning to a far-side place eases there, or jumps under reduced motion. MapLibre keeps the globe one size.
function turnTo(map, at) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) map.jumpTo({center: at});
  else map.easeTo({center: at, duration: 1000});
}

function placeNotes(map) {
  const cell = $('dm-map-cell');
  const layer = cell.querySelector('.dm-notes') || svg('svg', {class: 'dm-notes'}, cell);
  layer.replaceChildren();
  // The notes speak of the overview, so they step aside while one place is focused.
  if (focused) notes.forEach(n => Object.assign(n, {drawn: false, g: null, covers: [], why: 'the map shows one place\'s flows'}));
  if (!notes.length || focused) return;
  const scene = labelScene(map, labelPlan?.labels || [], labelPlan?.deck ?? !!pageLibs.deck);
  const names = drawnNames(map, scene), taken = names.map(n => n.box), line = scene.size * 1.25;
  // Land is every polygon the page draws: class areas, land, and base polygons; a basemap's water and the sphere's
  // ocean are polygons too, so they stay out.
  const areas = map.getStyle().layers.filter(l => l.type === 'fill' && l.source !== 'basemap' && !/-ocean$/.test(l.id)).map(l => l.id);
  const seen = new Map();
  const land = (x, y) => {
    const k = `${Math.round(x / 3)},${Math.round(y / 3)}`;
    if (!seen.has(k)) seen.set(k, map.queryRenderedFeatures([x, y], {layers: areas}).length > 0);
    return seen.get(k);
  };
  // The share of the box over land, from a grid of 8 by 3 points.
  const under = box => {
    if (!areas.length) return 0;
    let hit = 0;
    for (let i = 0; i < 8; i++) for (let j = 0; j < 3; j++) hit += land(box[0] + (i + 0.5) * (box[2] - box[0]) / 8, box[1] + (j + 0.5) * (box[3] - box[1]) / 3);
    return hit / 24;
  };
  for (const n of notes) {
    Object.assign(n, {drawn: false, far: false, box: null, g: null, covers: [], shown: n.text});
    if (!n.at) continue;
    const a = noteAnchor(map, n);
    if (!a) { n.why = 'its place is outside the view'; continue; }
    n.far = a.far;
    n.shown = a.far ? `${n.text} (far side)` : n.text;
    let best = null;
    for (const [k, width] of NOTE.widths.entries()) for (const reach of NOTE.reaches) for (const [, sx, sy] of CORNERS) {
      const rows = wrap(n.shown, width), w = Math.max(...rows.map(measure)), h = rows.length * line;
      const u = sx && sy ? Math.SQRT1_2 : 1, end = [a.p[0] + sx * u * (a.r + reach), a.p[1] + sy * u * (a.r + reach)];
      const x0 = sx > 0 ? end[0] + 2 : sx < 0 ? end[0] - 2 - w : end[0] - w / 2;
      const y0 = sy > 0 ? end[1] + 1 : sy < 0 ? end[1] - 1 - h : end[1] - h / 2;
      const box = [x0, y0, x0 + w, y0 + h], lead = {a: [a.p[0] + sx * u * a.r, a.p[1] + sy * u * a.r], b: end, hw: 0.5};
      let cost = reach / 2 + 4 * k + boxCost(box, scene, null) + 400 * taken.filter(t => boxesMeet(box, t, 2)).length + NOTE.area * under(box);
      cost += 100 * taken.filter(t => clippedLength(lead, t) > 0).length;
      cost += 100 * scene.circles.filter(k => k.key !== n.circle && segMeetsCircle(lead, k)).length;
      if (!best || cost < best.cost) best = {cost, box, lead, sx, rows};
    }
    if (best.cost >= 1000) { n.why = 'no corner around its place has room inside the map'; continue; }
    const {box, lead, sx, rows} = best, g = svg('g', {class: a.far ? 'dm-note dm-note-far' : 'dm-note'}, layer);
    svg('line', {x1: lead.a[0], y1: lead.a[1], x2: lead.b[0], y2: lead.b[1], class: 'dm-leader'}, g);
    if (!n.circle || a.far) svg('circle', {cx: a.p[0], cy: a.p[1], r: NOTE.dot, class: 'dm-leader-dot'}, g);
    const x = sx > 0 ? box[0] : sx < 0 ? box[2] : (box[0] + box[2]) / 2;
    const text = svg('text', {'text-anchor': sx > 0 ? 'start' : sx < 0 ? 'end' : 'middle'}, g);
    rows.forEach((row, i) => svg('tspan', {x, y: box[1] + line * (i + 0.5), dy: '0.35em'}, text, row));
    if (a.far) {
      for (const [k, v] of Object.entries({tabindex: 0, role: 'button', 'aria-label': `Turn the globe to ${n.text}`})) g.setAttribute(k, v);
      g.addEventListener('click', () => turnTo(map, n.at));
      g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); turnTo(map, n.at); } });
    }
    n.covers = names.filter(nm => boxesMeet(box, nm.box, 0) || clippedLength(lead, nm.box) > 0).map(nm => nm.text);
    Object.assign(n, {drawn: true, box, g, anchor: a.p});
    taken.push(box);
  }
}

// While the map moves, each note rides with its place; it hides when the place crosses the horizon or leaves the
// view, and every note is placed again when the move ends.
function moveNotes(map) {
  for (const n of notes) {
    if (!n.g) continue;
    const a = noteAnchor(map, n);
    n.g.style.display = a && a.far === n.far ? '' : 'none';
    if (a) n.g.setAttribute('transform', `translate(${a.p[0] - n.anchor[0]} ${a.p[1] - n.anchor[1]})`);
  }
}

// Per flows layer the reveal control moves: the flows it draws, of how many, the kept line, and the flows on the map.
function revealReport(map) {
  return Object.entries(ranks).map(([name, n]) => {
    const L = legend.layers[name], arcs = (live.arcs || []).find(a => a.name === name);
    const drawn = arcs ? arcs.layer.props.data.length
      : map.getLayer(name) ? new Set(map.queryRenderedFeatures({layers: [name]}).map(f => f.properties.dm_rank)).size : 0;
    return {layer: name, shown: n, of: L.reveal.count, note: $(`dm-kept-${name}`)?.textContent ?? null, drawn,
      label: document.querySelector(`label[for="dm-reveal-${name}"]`)?.textContent ?? null};
  });
}

function notesReport(map) {
  const at = map.getCanvas().getBoundingClientRect();
  return notes.map(n => ({text: n.shown ?? n.text, at: n.at, node: n.node, drawn: !!n.drawn, farSide: !!n.far, why: n.drawn ? null : n.why,
    covers: n.covers || [], box: n.box && {x: at.x + n.box[0], y: at.y + n.box[1], w: n.box[2] - n.box[0], h: n.box[3] - n.box[1]}}));
}

// ---------- flows over nodes they don't connect, measured on screen at the current view ----------

function distanceToSegment([x, y], a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1], t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy || 1)));
  return Math.hypot(a[0] + t * dx - x, a[1] + t * dy - y);
}

// Each drawn MapLibre flow line that passes over the circle of a node it doesn't connect: the circle's center lies
// nearer the line, moved by its dm_offset as MapLibre draws it, than the circle's radius plus half the line's width.
// The lever clears nodes in kilometers, which can fall short at the zoom the page opens on. Raised deck.gl arcs leave
// the ground, so they are left out.
function crossings(map) {
  const out = [], globe = spec.projection.type === 'globe';
  const center = map.getCenter().toArray(), horizon = globe ? horizonDeg(map) : Infinity;
  const front = c => !globe || angularKm(c, center) / EARTH_KM / RAD < horizon;
  const xy = c => { const p = map.project(c); return [p.x, p.y]; };
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows' || !map.getLayer(name)) continue;
    const f = filesOf(name, L), all = data[f.nodes]?.features || [];
    const names = Object.fromEntries(all.map(n => [n.properties.dm_key ?? n.id, n.properties.dm_label ?? n.id]));
    const nodes = all.filter(n => front(n.geometry.coordinates) && !nodeHidden(f.nodes, n))
      .map(n => ({key: n.properties.dm_key ?? n.id, c: xy(n.geometry.coordinates), r: n.properties.dm_r || 3}));
    for (const line of data[f.main]?.features || []) {
      const p = line.properties, hw = (p.dm_width || 1) / 2, off = p.dm_offset || 0, worst = new Map();
      if (!drawnFlow(name, p)) continue;
      for (const part of line.geometry.type === 'MultiLineString' ? line.geometry.coordinates : [line.geometry.coordinates]) {
        for (let i = 1; i < part.length; i++) {
          if (!front(part[i - 1]) || !front(part[i])) continue;
          const a = xy(part[i - 1]), b = xy(part[i]), len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
          // Right of travel on a screen whose y runs down.
          const nx = -(b[1] - a[1]) / len * off, ny = (b[0] - a[0]) / len * off;
          const a2 = [a[0] + nx, a[1] + ny], b2 = [b[0] + nx, b[1] + ny];
          for (const n of nodes) {
            if (n.key === p.dm_o || n.key === p.dm_d) continue;
            const over = n.r + hw - distanceToSegment(n.c, a2, b2);
            if (over > (worst.get(n.key) ?? 0)) worst.set(n.key, over);
          }
        }
      }
      for (const [key, px] of worst) {
        out.push({layer: name, flow: `${names[p.dm_o] ?? p.dm_o} to ${names[p.dm_d] ?? p.dm_d}`, node: names[key] ?? key, px: Math.round(px * 10) / 10});
      }
    }
  }
  return out.sort((a, b) => b.px - a.px);
}

// ---------- the report `datamap.py check` judges ----------

const rect = e => { const r = e.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height}; };
const family = s => String(s).split(',')[0].trim().replace(/^["']|["']$/g, '')
  .replace(/\s+(Regular|Medium|Bold|Italic|Light|Semibold|SemiBold|Black|Thin)(\s+Italic)?$/i, '');

function report(map, arcs) {
  const own = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const texts = [...document.body.querySelectorAll('*')].filter(e => !e.closest('script, style') && own(e) && e.getClientRects().length);
  const fonts = new Set(texts.map(e => family(getComputedStyle(e).fontFamily)));
  const sizes = new Set(texts.map(e => parseFloat(getComputedStyle(e).fontSize)));
  const style = map?.getStyle();
  for (const l of style?.layers || []) {
    if (l.source === 'basemap') continue;
    const font = l.layout?.['text-font'];
    if (l.type === 'symbol' && l.layout?.['text-field'] && Array.isArray(font) && typeof font[0] === 'string') fonts.add(family(font[0]));
    if (l.type === 'symbol' && typeof l.layout?.['text-size'] === 'number') sizes.add(l.layout['text-size']);
  }
  const side = $('dm-side') || document.querySelector('aside');
  const sideBox = side && rect(side);
  return {
    projection: map ? (map.getProjection()?.type || 'mercator') : null,
    pitch: map?.getPitch() ?? 0, bearing: map?.getBearing() ?? 0,
    zoom: map?.getZoom() ?? null, minZoom: map ? zoomLimits(map)[0] : null, maxZoom: map ? zoomLimits(map)[1] : null,
    center: map?.getCenter().toArray() ?? null,
    globe: spec.projection?.type === 'globe' && map ? {radius: globeScale(map)} : null,
    maxBounds: map?.getMaxBounds()?.toArray() ?? null,
    controls: [...new Set([...document.querySelectorAll('[class*="maplibregl-ctrl"]')].flatMap(e => [...e.classList])
      .filter(c => /^maplibregl-ctrl-/.test(c)))],
    fonts: [...fonts], fontSizes: [...sizes].sort((a, b) => a - b),
    legendEntries: [...document.querySelectorAll('[data-dm-color]')].map(e => ({layer: e.dataset.dmLayer, kind: e.dataset.dmKind,
      color: e.dataset.dmColor, label: e.dataset.dmLabel, expect: e.dataset.dmExpect === '1'})),
    moving: map ? map.isMoving() || map.isZooming() || map.isRotating() : false,
    layers: [...(style?.layers || []).map(l => ({id: l.id, type: l.type, source: l.source ?? null})),
      ...(arcs || []).map(a => ({id: a.name, type: 'deck:arc', source: filesOf(a.name, legend.layers[a.name]).main}))],
    sources: Object.entries(style?.sources || {}).map(([id, s]) => ({id, type: s.type, url: s.url ?? (typeof s.data === 'string' ? s.data : null)})),
    textBoxes: texts.map(e => ({text: e.textContent.trim().slice(0, 60), ...rect(e)})),
    clipped: sideBox ? texts.filter(e => e.closest('aside') && rect(e).y + rect(e).h > sideBox.y + sideBox.h + 1).map(e => e.textContent.trim().slice(0, 60)) : [],
    mapBox: map ? rect(map.getCanvas()) : null,
    chartBox: map ? null : sideBox,
    baseColors: baseColors(style),
    arcs: (arcs || []).map(a => ({layer: a.name, apex: a.apex, longestKm: a.longest, height: a.height})),
    arrows: arrowAgreement(map),
    labels: labelReport(map),
    annotations: map ? notesReport(map) : [],
    crossings: map ? crossings(map) : [],
    figure: figureSlack(),
    lead: map ? leadReport(map) : null,
    edgeCut: map ? edgeCut(map) : null,
    dmControls: [...document.querySelectorAll('[data-dm-control]')].map(e => e.dataset.dmControl),
    reveal: map ? revealReport(map) : [],
    focus: map ? focusReport(map) : null,
    hint: $('dm-hint')?.textContent ?? null,
    highlight: [...highlighted].map(key => ({key, name: highlightNames().get(key) ?? null,
      companions: document.querySelectorAll(`[data-dm-highlight="${CSS.escape(key)}"]`).length})),
    tooltips: !!document.querySelector('.dm-tip'),
    rendered: renderedCounts(map),
    viewport: {w: innerWidth, h: innerHeight, dpr: devicePixelRatio, scrollY}
  };
}

// How far each arrowhead turns from the screen direction of its own line's last segment, in degrees. Under a
// CRS the head draws at dm_screen; elsewhere MapLibre turns it to the bearing against local north, which is
// the screen direction of a short step along that bearing.
function arrowAgreement(map) {
  if (!map) return [];
  const c = map.getCenter().toArray(), {width: w, height: h} = map.getCanvas().getBoundingClientRect();
  const angle = (a, b) => { const p = map.project(a), q = map.project(b); return Math.atan2(q.x - p.x, p.y - q.y) / RAD; };
  const out = [];
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows') continue;
    const f = filesOf(name, L), lines = data[f.main]?.features || [], arrows = data[f.arrows]?.features || [];
    const layout = map.getStyle().layers.find(l => l.id === name + '-arrows')?.layout || {};
    const prop = Array.isArray(layout['icon-rotate']) ? layout['icon-rotate'][1] : null;
    // A map-aligned head turns from local north, which only Mercator keeps exactly; anything else is a screen angle.
    const drawn = layout['icon-rotation-alignment'] === 'map' && spec.projection.type === 'mercator' ? 'map' : prop;
    if (!drawn) continue;
    const rows = [];
    for (const a of arrows) {
      if (!drawnFlow(name, a.properties)) continue;
      const at = a.geometry.coordinates, p = map.project(at);
      if (p.x < 0 || p.y < 0 || p.x > w || p.y > h) continue;
      if (spec.projection.type === 'globe' && angularKm(at, c) > 0.42 * Math.PI * EARTH_KM) continue;
      const l = lines.find(x => x.properties.dm_o === a.properties.dm_o && x.properties.dm_d === a.properties.dm_d);
      if (!l) continue;
      const part = l.geometry.type === 'MultiLineString' ? l.geometry.coordinates.at(-1) : l.geometry.coordinates;
      const line = angle(part.at(-2), part.at(-1));
      const head = drawn === 'map' ? angle(at, destination(at, a.properties.dm_bearing, 0.05)) : a.properties[drawn];
      rows.push({o: a.properties.dm_o, d: a.properties.dm_d, off: Math.abs(((head - line + 540) % 360) - 180)});
    }
    const worst = rows.reduce((m, r) => r.off > (m?.off ?? -1) ? r : m, null);
    out.push({layer: name, checked: rows.length, of: arrows.length, maxOff: worst ? Math.round(worst.off * 10) / 10 : null,
      worst: worst ? `${worst.o} to ${worst.d}` : null});
  }
  return out;
}
// Features each legend layer has on screen, keyed the way legend entries are (nodes under LAYER-nodes).
function renderedCounts(map) {
  if (!map) return {};
  const out = {}, ids = new Set(map.getStyle().layers.map(l => l.id));
  for (const [name, L] of layersOf()) {
    for (const [key, id] of [[name, name], [name + '-nodes', name + '-nodes']]) {
      if (ids.has(id)) out[key] = map.queryRenderedFeatures({layers: [id]}).length;
    }
    if (L.kind === 'flows' && !ids.has(name)) out[name] = (data[filesOf(name, L).main]?.features || []).length;
  }
  for (const s of stems.filter(s => s.startsWith('base-'))) {
    out[s] = map.queryRenderedFeatures({layers: [s + '-fill', s + '-line'].filter(id => ids.has(id))}).length;
  }
  return out;
}
function angularKm([a, b], [c, d]) {
  const x = Math.sin(b * RAD) * Math.sin(d * RAD) + Math.cos(b * RAD) * Math.cos(d * RAD) * Math.cos((c - a) * RAD);
  return EARTH_KM * Math.acos(Math.min(1, Math.max(-1, x)));
}

function baseColors(style) {
  const ids = new Set((style?.layers || []).map(l => l.id));
  const has = re => [...ids].some(id => re.test(id));
  // Under a CRS the ocean is the sphere's fill, which dm-spec.frame "none" leaves out.
  const ocean = !!style && (spec.projection?.type !== 'crs' || has(/-ocean$/));
  return [['page', true], ['ocean', ocean], ['graticule', has(/-lines$/)], ['sphere-edge', has(/-edge$/)],
    ['land', ids.has('land') || has(/^base-.*-fill$/)], ['land-edge', ids.has('land-edge') || has(/^base-.*-outline$/)],
    ['base-line', has(/^base-.*-line$/)]].filter(([, on]) => on).map(([k]) => tok(k));
}

// A wide projection in a tall cell leaves bands above and below the map; give the map row the map's own
// height and center the figure on the page instead.
// A static figure is an image of one size, so the page lays itself out at dm-spec.figure.size in any window,
// one column when that is narrow.
function layOutFigure() {
  const size = /^(\d+)x(\d+)$/.exec(spec.figure?.size || '');
  if (!size) return;
  document.body.classList.add('dm-figure');
  document.body.classList.toggle('dm-narrow', Number(size[1]) <= 720);
  Object.assign(document.body.style, {width: `${size[1]}px`, height: `${size[2]}px`});
}

// A static figure keeps its size, so its map row hugs the map and any height left over falls below the source line,
// where the report measures it.
function hugMap(map) {
  // The hint line sits in the map's cell, under the map.
  const cell = $('dm-map-cell'), w = cell.clientWidth, below = cell.clientHeight - $('map').clientHeight, h = cell.clientHeight - below;
  const figure = !!spec.figure?.size, narrow = document.body.classList.contains('dm-narrow');
  if (spec.projection.type === 'globe' || (!figure && innerWidth <= 720)) return false;
  const xy = boxEdge(fitBox(thematicPoints())).map(p => map.project(p)), xs = xy.map(p => p.x), ys = xy.map(p => p.y);
  const aspect = (Math.max(...xs) - Math.min(...xs)) / (Math.max(...ys) - Math.min(...ys));
  const aside = $('dm-side'), top = aside ? aside.getBoundingClientRect().top : 0;
  const side = aside && !narrow ? Math.max(0, ...[...aside.querySelectorAll('section')].map(e => e.getBoundingClientRect().bottom - top)) : 0;
  const pad = fitPad(), want = Math.max(Math.ceil((w - 2 * pad) / aspect) + 2 * pad, side);
  if (want >= h - 8) return false;
  const row = want + below;
  // The page starts at the top, as any page does, and the height left over falls below the source line.
  document.body.style.alignContent = 'start';
  if (figure) {
    document.body.style.gridTemplateRows = narrow ? `auto ${row}px auto auto` : `auto ${row}px auto`;
  } else {
    document.body.style.height = 'auto';
    document.body.style.minHeight = '100%';
    document.body.style.gridTemplateRows = `auto ${row}px auto`;
  }
  map.resize();
  return true;
}

// How much of the page the map takes: its canvas, the part of it the data's extent draws on (the globe's disk, or
// the fitted box), and every block around it, named, for check to say what crowds the map.
function leadReport(map) {
  const canvas = rect(map.getCanvas()), {clientWidth: W, clientHeight: H} = map.getCanvas();
  let xs, ys;
  if (spec.projection.type === 'globe') {
    const c = map.project(map.getCenter()), r = globeScale(map);
    xs = [c.x - r, c.x + r]; ys = [c.y - r, c.y + r];
  } else {
    const xy = boxEdge(fitBox(thematicPoints())).map(q => map.project(q));
    xs = xy.map(q => q.x); ys = xy.map(q => q.y);
  }
  const clip = (v, hi) => Math.min(Math.max(v, 0), hi);
  const x0 = clip(Math.min(...xs), W), x1 = clip(Math.max(...xs), W), y0 = clip(Math.min(...ys), H), y1 = clip(Math.max(...ys), H);
  const blocks = [];
  const add = (e, what) => { if (e?.getClientRects().length) blocks.push({what, ...rect(e)}); };
  const titled = (sec, kind) => `${kind} "${(sec.querySelector('h2')?.textContent || sec.querySelector('h3')?.textContent || '').slice(0, 48)}"`;
  add(document.querySelector('header'), 'the title block');
  for (const sec of document.querySelectorAll('#dm-legend > section')) add(sec, titled(sec, 'the legend'));
  for (const sec of document.querySelectorAll('#dm-companions > section')) add(sec, titled(sec, 'the companion'));
  add(document.querySelector('footer'), 'the source line');
  return {canvas, drawn: {x: canvas.x + x0, y: canvas.y + y0, w: x1 - x0, h: y1 - y0}, blocks};
}

// The empty page below a static figure's source line, in px: the height its size asks for and nothing fills.
function figureSlack() {
  if (!spec.figure?.size) return null;
  const body = document.body.getBoundingClientRect(), foot = document.querySelector('footer')?.getBoundingClientRect();
  const pad = parseFloat(getComputedStyle(document.body).paddingBottom) || 0;
  return {w: Math.round(body.width), h: Math.round(body.height), slack: Math.max(0, Math.round(body.bottom - pad - (foot ? foot.bottom : body.bottom)))};
}

// ---------- focus: one node's flows, out and in apart, its partners ranked, and the title rewritten for it ----------

const FOCUS_SAYS = {out: ['leave', 'go to'], in: ['reach', 'come from'], both: ['travel to and from', 'are with']};
const PARTNER_ROWS = 12;

// Totals and partners of KEY in its layer's file, ranked by dm-spec.focus.by: out, in, or both (the default).
function focusStats(name, key) {
  const L = legend.layers[name], f = filesOf(name, L), by = FOCUS_SAYS[spec.focus?.by] ? spec.focus.by : 'both';
  const names = Object.fromEntries((data[f.nodes]?.features || []).map(n => [n.properties.dm_key, String(n.properties.dm_label ?? n.properties.dm_key)]));
  const partners = new Map();
  let out = 0, inn = 0, flows = 0;
  for (const {properties: p} of data[f.main]?.features || []) {
    if (!touches(p, key)) continue;
    const away = p.dm_o === key, other = away ? p.dm_d : p.dm_o, v = p.dm_value || 0;
    const row = partners.get(other) ?? {key: other, name: names[other] ?? other, out: 0, in: 0};
    row[away ? 'out' : 'in'] += v;
    partners.set(other, row);
    if (away) out += v; else inn += v;
    flows++;
  }
  const value = r => by === 'out' ? r.out : by === 'in' ? r.in : r.out + r.in;
  const ranked = [...partners.values()].filter(r => value(r) > 0).sort((a, b) => value(b) - value(a) || a.name.localeCompare(b.name));
  const total = by === 'out' ? out : by === 'in' ? inn : out + inn;
  // The file holds every flow only when the lever wrote them all, with --reveal and a --reveal-max past the count.
  const held = (data[f.main]?.features || []).length;
  return {layer: name, key, name: names[key] ?? key, unit: L.unit || 'flows', by, out, in: inn, total, flows, ranked, value,
    complete: held >= (L.total ?? held), held, all: L.total ?? held};
}

const percent = x => x < 0.005 ? 'under 1%' : `${Math.round(100 * x)}%`;
function focusText(s) {
  const top = s.ranked[0], [verb, prep] = FOCUS_SAYS[s.by];
  if (!top) return {title: s.name, subtitle: `No ${s.unit} ${s.by === 'both' ? 'to or from' : verb} ${s.name} in these flows.`};
  const vars = {name: s.name, top: top.name, top_value: fmt(s.value(top)), share: percent(s.value(top) / s.total), total: fmt(s.total),
    out: fmt(s.out), in: fmt(s.in), partners: fmt(s.ranked.length), unit: s.unit};
  const fill = text => String(text).replace(/\{(\w+)\}/g, (m, k) => k in vars ? vars[k] : m);
  return {title: fill(spec.focus?.title ?? '{name}'),
    subtitle: fill(spec.focus?.subtitle ?? `{total} {unit} ${verb} {name}; the most ${prep} {top}, {top_value} ({share})`)};
}

const focusColor = key => ['case', ['==', ['get', 'dm_o'], key], tok('out'), tok('in')];
let overviewText = null;

// The partners panel stands in for the companions, which speak of the overview, with a key to the two colors.
function focusPanel(s) {
  const companions = $('dm-companions');
  $('dm-focus-panel')?.remove();
  if (companions) companions.hidden = !!s;
  if (!s) return;
  const sec = html('section', {id: 'dm-focus-panel', class: 'dm-companion'});
  (companions || $('dm-legend')).before(sec);
  html('h2', {}, sec, `Flows to and from ${s.name}`);
  const step = parseFloat(tok('t4')) * 1.7, k = svg('svg', {width: '100%', height: 2 * step}, sec);
  [[tok('out'), `Leaving ${s.name}`], [tok('in'), `Arriving at ${s.name}`]].forEach(([c, text], i) => {
    const y = (i + 0.5) * step;
    // check judges the overview, so the key asks nothing of the render's colors.
    mark(svg('line', {x1: 0, x2: 20, y1: y, y2: y, stroke: c, 'stroke-width': 3}, k), s.layer, 'focus', c, text, false);
    svg('polygon', {points: `20,${y - 4} 28,${y} 20,${y + 4}`, fill: c}, k);
    label(k, 36, y, text);
  });
  const table = html('table', {class: 'dm-table'}, sec), head = html('tr', {}, html('thead', {}, table));
  ['Place', 'Out', 'In'].forEach((h, i) => html('th', i ? {class: 'dm-num'} : {}, head, h));
  const body = html('tbody', {}, table);
  for (const r of s.ranked.slice(0, PARTNER_ROWS)) {
    const row = html('tr', {}, body);
    [r.name, r.out, r.in].forEach((v, i) => html('td', i ? {class: 'dm-num'} : {}, row, fmt(v)));
  }
  if (s.ranked.length > PARTNER_ROWS) html('p', {class: 'dm-note'}, sec, `and ${s.ranked.length - PARTNER_ROWS} more places`);
}

// Focuses KEY, or returns to the overview for null. The map moves only to bring a focused place into view.
function setFocus(key) {
  if (!focusLayer) return Promise.resolve();
  const L = legend.layers[focusLayer], nodes = data[filesOf(focusLayer, L).nodes]?.features || [];
  const node = nodes.find(n => n.properties.dm_key === key);
  focused = node ? {layer: focusLayer, key} : null;
  const s = focused && focusStats(focusLayer, key);
  const text = s ? focusText(s) : overviewText;
  for (const [id, v] of [['dm-title', text.title], ['dm-subtitle', text.subtitle]]) if ($(id)) $(id).textContent = v;
  const pick = $('dm-focus-pick'), reset = $('dm-focus-reset');
  if (pick) pick.value = focused ? key : '';
  if (reset) reset.hidden = !focused;
  const note = $(`dm-kept-${focusLayer}`), slider = $(`dm-reveal-${focusLayer}`);
  if (note) note.textContent = s ? `${fmt(s.flows)} flows to and from ${s.name}` + (s.complete ? '' : `, among the ${fmt(s.held)} largest of ${fmt(s.all)}`)
    : overviewNote(focusLayer, L);
  if (slider) slider.disabled = !!focused;
  focusPanel(s);
  applyView();
  const map = live.map;
  if (map && node && !inView(map, node.geometry.coordinates)) turnTo(map, node.geometry.coordinates);
  return replaceNames();
}

function inView(map, at) {
  const {clientWidth: W, clientHeight: H} = map.getCanvas(), p = map.project(at);
  const front = spec.projection.type !== 'globe' || angularKm(at, map.getCenter().toArray()) / EARTH_KM / RAD < horizonDeg(map);
  return front && p.x >= 0 && p.y >= 0 && p.x <= W && p.y <= H;
}

// The picker under the subtitle lists every node of the focused layer by name; a node's circle focuses it on a click
// or a tap, a second click or Escape returns to the overview, and so does the reset button or "every place". It is
// built before the map, whose fitted view would shift once the header grew.
function focusPicker() {
  if (!focusLayer) return;
  overviewText = {title: $('dm-title')?.textContent ?? '', subtitle: $('dm-subtitle')?.textContent ?? ''};
  const L = legend.layers[focusLayer];
  const nodes = (data[filesOf(focusLayer, L).nodes]?.features || []).map(n => [n.properties.dm_key, String(n.properties.dm_label ?? n.properties.dm_key)])
    .sort((a, b) => a[1].localeCompare(b[1]));
  const box = html('div', {class: 'dm-focus', 'data-dm-control': 'focus'});
  ($('dm-subtitle') || $('dm-title'))?.after(box);
  html('label', {for: 'dm-focus-pick'}, box, spec.focus?.label ?? 'Show the flows of');
  const pick = html('select', {id: 'dm-focus-pick'}, box);
  html('option', {value: ''}, pick, 'every place');
  for (const [key, name] of nodes) html('option', {value: key}, pick, name);
  const reset = html('button', {type: 'button', id: 'dm-focus-reset', hidden: ''}, box, 'Show all');
  pick.addEventListener('change', () => setFocus(pick.value || null));
  reset.addEventListener('click', () => setFocus(null));
  addEventListener('keydown', e => { if (e.key === 'Escape' && focused) setFocus(null); });
}
function focusClicks(map) {
  if (!focusLayer) return;
  map.on('click', focusLayer + '-nodes', e => {
    const key = e.features[0]?.properties.dm_key;
    if (key != null) setFocus(focused?.key === key ? null : key);
  });
}

function focusReport(map) {
  if (!focusLayer) return null;
  const s = focused && focusStats(focused.layer, focused.key), arcs = (live.arcs || []).find(a => a.name === focusLayer);
  const drawn = arcs ? arcs.layer.props.data.length
    : map.getLayer(focusLayer) ? new Set(map.queryRenderedFeatures({layers: [focusLayer]}).map(f => `${f.properties.dm_o}>${f.properties.dm_d}`)).size : 0;
  return {layer: focusLayer, choices: Math.max(0, ($('dm-focus-pick')?.options.length ?? 1) - 1), key: focused?.key ?? null, name: s?.name ?? null,
    title: $('dm-title')?.textContent ?? null, subtitle: $('dm-subtitle')?.textContent ?? null, drawn,
    note: $(`dm-kept-${focusLayer}`)?.textContent ?? null, colors: s ? {out: tok('out'), in: tok('in')} : null,
    partners: s ? s.ranked.map(r => ({key: r.key, name: r.name, out: r.out, in: r.in})) : []};
}

// ---------- the hint: one quiet line under an interactive map saying what a reader can do with it ----------

// From dm-spec and the map's own handlers: hover or tap for numbers, click a place to focus it, drag to pan or turn,
// zoom, and tilt when the map allows it. dm-spec.hint replaces the line with its own words, and false leaves it off;
// a static figure has none.
function hintText(map) {
  if (spec.hint === false || spec.figure?.size || !spec.projection) return '';
  if (typeof spec.hint === 'string') return spec.hint;
  const said = [], z = spec.zoom || {};
  if (spec.tooltips !== false && layersOf().length) said.push('hover or tap for numbers');
  if (focusLayer) said.push('click or tap a place for its flows alone, Esc to go back');
  said.push(spec.projection.type === 'globe' ? 'drag to turn the globe' : 'drag to pan');
  if (!(z.min != null && z.min === z.max)) said.push('scroll or pinch to zoom');
  if (map && map.getMaxPitch() > map.getMinPitch() && (map.dragRotate.isEnabled() || map.touchPitch.isEnabled())) said.push('right-drag to tilt');
  const line = said.join('; ');
  return line[0].toUpperCase() + line.slice(1) + '.';
}

// Written before the map exists, so the map's cell leaves the line its room; after the page's own extension runs,
// the line is written again, and if it grew, the map resizes.
function drawHint(map) {
  const text = hintText(map), cell = $('dm-map-cell');
  let hint = $('dm-hint');
  if (!text) { hint?.remove(); $('map').style.bottom = ''; return false; }
  hint ??= html('p', {id: 'dm-hint', class: 'dm-hint'}, cell);
  const before = hint.offsetHeight;
  hint.textContent = text;
  $('map').style.bottom = `${hint.offsetHeight + 6}px`;
  return hint.offsetHeight !== before;
}

// ---------- start ----------

// The pinned libraries sync copied into vendor/, as the head's tags loaded them. Chrome loads no ES module from a
// file, so MapLibre, its worker, and proj4 arrive as text and run from blob URLs; deck.gl, pmtiles, and the
// Protomaps basemaps are classic scripts that define their globals.
async function libs() {
  const text = self.dmVendor || {}, out = {};
  const blob = source => URL.createObjectURL(new Blob([source], {type: 'text/javascript'}));
  if (text['maplibre-gl']) {
    out.maplibregl = await import(blob(text['maplibre-gl']));
    out.maplibregl.setWorkerUrl(blob(text['maplibre-gl-worker']));
  }
  if (text.proj4) {
    await import(blob(text.proj4));
    Object.assign(out, {proj4: self.proj4, proj4Source: text.proj4});
  }
  for (const name of ['deck', 'pmtiles', 'basemaps']) if (self[name]) out[name] = self[name];
  return out;
}

const once = (target, event) => new Promise(r => target.once(event, r));

async function start(libs, extend) {
  pageLibs = libs;
  [...new Set([...Object.keys(ranks), ...(focusLayer ? [focusLayer] : [])])].forEach(updateShownKeys);
  document.body.classList.toggle('dm-chart', !spec.projection);
  layOutFigure();
  drawLegend();
  drawCompanions();
  focusPicker();
  drawHint(null);
  if (!spec.projection) {
    window.dataMap.report = () => report(null, null);
    await document.fonts.ready;
    resolveReady();
    return;
  }
  const {maplibregl, deck} = libs;
  const proj = spec.projection, crs = proj.type === 'crs';
  const missing = [['MapLibre GL JS', maplibregl], ['proj4', !crs || libs.proj4]].filter(([, lib]) => !lib).map(([name]) => name);
  if (missing.length) throw new Error(`vendor/ holds no ${missing.join(' or ')}, which this page draws with; run datamap.py sync on its folder`);
  if (crs) await registerCrs(maplibregl, libs.proj4, libs.proj4Source, proj);
  if (libs.pmtiles) maplibregl.addProtocol('pmtiles', new libs.pmtiles.Protocol().tile);
  const t = Object.fromEntries(['page', 'ocean', 'graticule', 'sphere-edge', 'land', 'land-edge', 'base-line', 'flow', 'node', 'symbol', 'text', 'rule']
    .map(k => [k, tok(k)]));
  const {style, hover, labels} = buildStyle(libs, t);
  resolveNotes();
  const map = new maplibregl.Map({container: 'map', style, attributionControl: {compact: true},
    pitch: spec.pitch || 0, maxPitch: spec.pitch || 0, dragRotate: false, pitchWithRotate: false, touchPitch: false,
    renderWorldCopies: false, fadeDuration: 0});
  map.touchZoomRotate.disableRotation();
  map.keyboard.disableRotation();
  map.setMissingStyleImageResolver(id => {
    const [make, options] = IMAGES[id] || [];
    if (make && !map.hasImage(id)) map.addImage(id, make(), options);
  });
  // A .pmtiles archive needs a server that answers Range requests, so a page opened from a file draws without it.
  let basemapMissing = false;
  map.on('error', e => {
    if (e.sourceId !== 'basemap' || location.protocol !== 'file:') return rejectReady(e.error || new Error(String(e)));
    if (!basemapMissing) console.warn(`the basemap ${e.source?.url ?? ''} can't load from a file, so the map draws without it; open the page from a web server to see it`);
    basemapMissing = true;
  });
  await once(map, 'load');
  fitView(map);
  if (hugMap(map)) fitView(map);
  screenArrows(map);
  // Panning a globe turns every place's north on screen; Mercator and a CRS keep their angles under pan and zoom.
  if (proj.type === 'globe') map.on('move', () => screenArrows(map));
  const show = spec.tooltips === false ? () => {} : interact(map, hover);
  let arcs = null, drawn = Promise.resolve(), overlay = null;
  if (deck) {
    let frame;
    drawn = new Promise(r => { frame = r; });
    arcs = arcLayers(deck, t, show);
    Object.assign(live, {arcs, t, show});
    overlay = new deck.MapLibreOverlay({interleaved: true, layers: arcs.map(a => a.layer), pickingRadius: HIT / 2,
      onAfterRender: () => frame(), onError: err => rejectReady(err)});
    map.addControl(overlay);
  }
  Object.assign(live, {map, overlay, t, show});
  focusClicks(map);
  swipeScrolls(map);
  window.dataMap.focus = key => setFocus(key);
  await placeLabels(map, labels, !!deck);
  placeNotes(map);
  map.on('move', () => moveNotes(map));
  map.on('moveend', () => placeNotes(map));
  if (extend) await extend({map, overlay, layers: (arcs || []).map(a => a.layer), data, spec, legend, libs});
  if (drawHint(map)) map.resize();
  map.triggerRepaint();
  await Promise.all([once(map, 'idle'), drawn]);
  window.dataMap.report = () => report(map, live.arcs || arcs);
  window.dataMap.map = map;
  await document.fonts.ready;
  resolveReady();
}

window.DataMap = {spec, data, legend, libs: () => libs().catch(err => { rejectReady(err); throw err; }),
  start: (libs, extend) => start(libs, extend).catch(err => { rejectReady(err); throw err; })};
})();
