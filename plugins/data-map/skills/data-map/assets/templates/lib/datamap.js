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
const ARROW = {len: 20, base: 19, pad: 4};
const ARC_APEX = 0.08;
const METHOD = {quantile: k => `${k} quantile classes`, jenks: k => `${k} classes by natural breaks (Jenks)`,
  equal: k => `${k} equal-interval classes`, stddev: k => `${k} classes by standard deviation from the mean`,
  headtail: k => `${k} classes by head/tail breaks`, manual: k => `${k} classes set by hand`};
const LABEL_ANCHORS = ['bottom-left', 'top-left', 'bottom-right', 'top-right', 'bottom', 'top', 'left', 'right'];

const $ = id => document.getElementById(id);
const parse = id => { const e = $(id); return e ? JSON.parse(e.textContent) : null; };
const spec = parse('dm-spec') || {};
const stems = [...document.querySelectorAll('script[id^="dm-data-"]')].map(e => e.id.slice(8));
const data = Object.fromEntries(stems.map(s => [s, parse('dm-data-' + s)]));
const legend = data.legend || {layers: {}};
const layersOf = () => Object.entries(legend.layers || {});
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
let measurer;
function measure(text) {
  measurer ??= document.createElement('canvas').getContext('2d');
  measurer.font = `${tok('t4')} ${tok('font')}`;
  return measurer.measureText(String(text)).width;
}
function fit(text, width) {
  text = String(text);
  if (measure(text) <= width) return text;
  while (text.length > 1 && measure(text + '…') > width) text = text.slice(0, -1);
  return text + '…';
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
    const top = colors.length * sh + (extra.length ? 10 : 0);
    const s = svg('svg', {width: '100%', height: top + extra.length * (sh + 6)}, sec);
    const pattern = svg('pattern', {id: `dm-hatch-${name}`, width: 6, height: 6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)'}, svg('defs', {}, s));
    svg('line', {x1: 0, y1: 0, x2: 0, y2: 6, stroke: 'rgba(40,40,40,0.5)', 'stroke-width': 1.2}, pattern);
    colors.forEach((c, i) => {
      mark(svg('rect', {x: 0, y: i * sh, width: sw, height: sh, fill: c}, s), name, 'class', c, labels[i], (counts[i] ?? 1) > 0);
      label(s, sw + gap, i * sh + sh / 2, labels[i] ?? '');
    });
    extra.forEach((x, j) => {
      const y = top + j * (sh + 6);
      if (x.hatch) {
        svg('rect', {x: 0, y, width: sw, height: sh, fill: tok('page'), stroke: tok('rule'), 'stroke-width': 0.5}, s);
        svg('rect', {x: 0, y, width: sw, height: sh, fill: `url(#dm-hatch-${name})`}, s);
      } else {
        mark(svg('rect', {x: 0, y, width: sw, height: sh, fill: x.color}, s), name, x.kind, x.color, x.text, x.expect);
      }
      label(s, sw + gap, y + sh / 2, x.text);
    });
    if (L.method) html('p', {class: 'dm-note'}, sec, (METHOD[L.method] || (k => `${k} classes, ${L.method}`))(L.k || colors.length));
  },
  sizes(sec, name, L) {
    nested(sec, name, L.legend_values || [], L.legend_radii || [], L.color || firstFill(name) || tok('symbol'));
  },
  flows(sec, name, L) {
    const values = L.legend_values || [], widths = L.legend_widths || [];
    const color = L.color || firstFill(filesOf(name, L).main) || tok('flow');
    const head = w => Math.max((L.arrow?.ratio ?? 2.5) * w, L.arrow?.min_px ?? 6);
    const run = 44, longest = Math.max(0, ...widths.map(head));
    const rows = widths.map((w, i) => ({w, v: values[i], len: head(w), h: Math.max(head(w) * ARROW.base / ARROW.len, 12)}));
    const s = svg('svg', {width: '100%', height: rows.reduce((a, r) => a + r.h + 6, 0)}, sec);
    let y = 0;
    for (const r of rows) {
      const cy = y + r.h / 2, half = r.len * ARROW.base / ARROW.len / 2;
      mark(svg('line', {x1: 0, x2: run + 0.5, y1: cy, y2: cy, stroke: color, 'stroke-width': r.w}, s), name, 'flow', color, fmt(r.v), true);
      svg('polygon', {points: `${run},${cy - half} ${run + r.len},${cy} ${run},${cy + half}`, fill: color}, s);
      label(s, run + longest + 10, cy, fmt(r.v));
      y += r.h + 6;
    }
    if (L.omitted_note) html('p', {class: 'dm-note'}, sec, L.omitted_note);
    const nodes = data[filesOf(name, L).nodes]?.features || [];
    const sized = nodes.filter(n => n.properties.dm_r > 0 && n.properties.dm_value > 0);
    if (sized.length > 1) {
      html('h3', {}, sec, L.nodes?.title || `Circle area: all ${L.unit || 'flows'} in and out`);
      const top = sized.reduce((a, n) => n.properties.dm_value > a.properties.dm_value ? n : a);
      const rmax = top.properties.dm_r, vmax = top.properties.dm_value;
      const values = L.nodes?.legend_values || niceSteps(vmax);
      const radii = L.nodes?.legend_radii || values.map(v => rmax * Math.sqrt(v / vmax));
      nested(sec, name + '-nodes', values, radii, top.properties.dm_fill || tok('node'));
    }
  }
};

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
  const rmax = Math.max(...radii), cx = rmax + 1, lx = 2 * rmax + 18, step = parseFloat(tok('t4')) + 2;
  const rows = values.map((v, i) => ({v, r: radii[i]})).sort((a, b) => b.r - a.r);
  let base = 2 * rmax + 2;
  // Labels sit at each circle's top, pushed apart where small circles crowd them, with a leader to each top.
  rows.forEach((row, i) => { row.y = Math.max(base - 2 * row.r, i ? rows[i - 1].y + step : -Infinity); });
  const below = Math.max(0, rows.at(-1).y + step / 2 - base);
  const s = svg('svg', {width: '100%', height: base + below + 2}, sec);
  for (const {v, r, y} of rows) {
    mark(svg('circle', {cx, cy: base - r, r, fill: color, stroke: tok('page'), 'stroke-width': 0.75}, s), layer, 'size', color, fmt(v), true);
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
    const labelW = Math.min(W * 0.42, Math.max(...rows.map(r => measure(r.label))) + 8);
    const valueW = Math.max(...rows.map(r => measure(fmt(r.value)))) + 6;
    const scale = (W - labelW - valueW) / Math.max(...rows.map(r => r.value), 1e-9);
    const s = svg('svg', {width: W, height: rows.length * (bh + gap) - gap}, sec);
    rows.forEach((r, i) => {
      const y = i * (bh + gap), w = Math.max(r.value * scale, 1);
      label(s, labelW - 8, y + bh / 2, fit(r.label, labelW - 8), {'text-anchor': 'end'});
      svg('rect', {x: labelW, y, width: w, height: bh, fill: tok('chart')}, s);
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
    if ((x + y) % 12 < 2) px.set([40, 40, 40, 120], (y * s + x) * 4);
  }
  return {width: s, height: s, data: px};
}
const IMAGES = {'dm-arrow': [arrowImage, {pixelRatio: 2, sdf: true}], 'dm-hatch': [hatchImage, {pixelRatio: 2}]};

// ---------- map layers, one builder per legend kind ----------

function prepArrows(fc) {
  for (const f of fc.features) {
    const p = f.properties, size = (p.dm_arrow || 8) / ARROW.len;
    p.dm_icon_size = size;
    p.dm_icon_offset = [0, -ARROW.pad + ((p.dm_setback || 0) + 1) / size];
    p.dm_screen = p.dm_bearing;
  }
}

function labelLayer(id, source, t) {
  const size = parseFloat(tok('t4'));
  return {id, type: 'symbol', source,
    layout: {'text-field': ['get', 'dm_label'], 'text-font': fontStack(), 'text-size': size,
      'text-variable-anchor': LABEL_ANCHORS, 'text-radial-offset': ['+', 0.25, ['/', ['coalesce', ['get', 'dm_r'], 3], size]],
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
        {id: name, type: 'circle', source: name, paint: {'circle-radius': 4.5, 'circle-color': fill, 'circle-stroke-color': t.page, 'circle-stroke-width': 0.75}},
        {id: name + '-hover', type: 'circle', source: name, filter: NONE, paint: {'circle-radius': 4.5, 'circle-opacity': 0, 'circle-stroke-color': t.text, 'circle-stroke-width': 1.5}}]};
      return {sources: {[name]: fc}, hover: [[name, name + '-hover']], fill: [
        {id: name, type: 'fill', source: name, paint: {'fill-color': fill}},
        {id: name + '-low-n', type: 'fill', source: name, filter: ['==', ['get', 'dm_low_n'], true], paint: {'fill-pattern': 'dm-hatch'}},
        {id: name + '-edge', type: 'line', source: name, paint: {'line-color': t.page, 'line-width': 0.5}},
        {id: name + '-hover', type: 'line', source: name, filter: NONE, paint: {'line-color': t.text, 'line-width': 1.5}}]};
    },
    sizes(name, L) {
      const fc = data[name];
      if (!fc) return {};
      return {sources: {[name]: fc}, hover: [[name, name + '-hover']], label: [labelLayer(name + '-labels', name, t)], point: [
        {id: name, type: 'circle', source: name, layout: {'circle-sort-key': ['get', 'dm_order']},
          paint: {'circle-radius': ['get', 'dm_r'], 'circle-color': ink(L.color || t.symbol), 'circle-stroke-color': t.page, 'circle-stroke-width': 0.75}},
        {id: name + '-hover', type: 'circle', source: name, filter: NONE,
          paint: {'circle-radius': ['get', 'dm_r'], 'circle-opacity': 0, 'circle-stroke-color': t.text, 'circle-stroke-width': 1.5}}]};
    },
    flows(name, L) {
      const f = filesOf(name, L), lines = data[f.main], nodes = data[f.nodes], arrows = data[f.arrows];
      const part = {sources: {}, hover: [], line: [], point: [], arrow: [], label: []};
      const color = ink(L.color || t.flow);
      if (lines && !deck) {
        part.sources[f.main] = lines;
        part.line.push(
          {id: name, type: 'line', source: f.main, layout: {'line-sort-key': ['get', 'dm_order'], 'line-join': 'round'},
            paint: {'line-color': color, 'line-width': ['get', 'dm_width']}},
          {id: name + '-hover', type: 'line', source: f.main, filter: NONE,
            paint: {'line-color': t.text, 'line-width': 1, 'line-gap-width': ['get', 'dm_width']}});
        part.hover.push([name, name + '-hover']);
      }
      if (nodes) {
        part.sources[f.nodes] = nodes;
        part.point.push(
          {id: name + '-nodes', type: 'circle', source: f.nodes, layout: {'circle-sort-key': ['get', 'dm_order']},
            paint: {'circle-radius': ['coalesce', ['get', 'dm_r'], 3], 'circle-color': ink(t.node), 'circle-stroke-color': t.page, 'circle-stroke-width': 1}},
          {id: name + '-nodes-hover', type: 'circle', source: f.nodes, filter: NONE,
            paint: {'circle-radius': ['coalesce', ['get', 'dm_r'], 3], 'circle-opacity': 0, 'circle-stroke-color': t.text, 'circle-stroke-width': 1.5}});
        part.label.push(labelLayer(name + '-labels', f.nodes, t));
        part.hover.push([name + '-nodes', name + '-nodes-hover']);
      }
      if (arrows) {
        prepArrows(arrows);
        part.sources[f.arrows] = arrows;
        // Each head turns to a screen angle measured from projected points (screenArrows). A bearing is not a
        // screen angle under a non-conformal CRS, and MapLibre's map-aligned icons drift from local north on the
        // globe away from the view's center (11 to 88 degrees in a pixel test at 55 to 72 degrees out).
        part.arrow.push({id: name + '-arrows', type: 'symbol', source: f.arrows,
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
  for (const s of ['frame', 'sphere', 'graticule'].filter(s => data[s])) {
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
  const kinds = buildKinds(t, crs, !!libs.deck);
  for (const [name, L] of layersOf()) {
    const part = kinds[L.kind]?.(name, L) || {};
    for (const [id, fc] of Object.entries(part.sources || {})) sources[id] = {type: 'geojson', data: fc};
    for (const g of Object.keys(groups)) groups[g].push(...(part[g] || []));
    hover.push(...(part.hover || []));
  }
  const style = {version: 8, projection: crs ? {type: proj.name} : {type: proj.type}, sources,
    layers: Object.values(groups).flat()};
  return {style, hover};
}

async function registerCrs(maplibregl, proj4, url, p) {
  const handler = new Blob([`import proj4 from '${url}';\nself.setProjectionHandler(definition => proj4(definition));\n`], {type: 'text/javascript'});
  await maplibregl.importScriptInWorkers(URL.createObjectURL(handler));
  const projection = proj4('EPSG:4326', p.definition);
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
function fitView(map) {
  const type = spec.projection.type, pts = thematicPoints();
  const pad = 14 + Math.max(0, ...layersOf().flatMap(([name, L]) => [name, filesOf(name, L).nodes])
    .flatMap(s => (data[s]?.features || []).map(f => f.properties?.dm_r || 0)));
  const {clientWidth: w, clientHeight: h} = map.getContainer();
  map.setMinZoom(null);
  map.setMaxZoom(null);
  map.setMaxBounds(null);
  let fitted;
  if (type === 'globe') {
    const center = Array.isArray(spec.center) ? spec.center : meanCenter(pts);
    map.jumpTo({center, zoom: 1.5});
    for (let i = 0; i < 3; i++) map.setZoom(map.getZoom() + Math.log2((Math.min(w, h) / 2 - pad) / globeRadius(map, center)));
  } else {
    const e = spec.extent;
    const b = e === 'world' ? [[-180, -90], [180, 90]] : Array.isArray(e) ? [[e[0], e[1]], [e[2], e[3]]] : bbox(pts.length ? pts : [[-180, -90], [180, 90]]);
    map.fitBounds(b, {padding: pad, animate: false});
    fitted = b;
  }
  const z0 = map.getZoom();
  const zoomOf = v => typeof v === 'number' ? v : typeof v === 'string' && /^fit([+-]\d+(\.\d+)?)?$/.test(v) ? z0 + Number(v.slice(3) || 0) : null;
  const zmin = zoomOf(spec.zoom?.min), zmax = zoomOf(spec.zoom?.max);
  if (zmin != null) map.setMinZoom(zmin);
  if (zmax != null) map.setMaxZoom(zmax);
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
  for (const [layer, outline] of hover) {
    map.on('mousemove', layer, e => {
      const f = e.features[0];
      map.setFilter(outline, ['==', ['id'], f.id ?? '__dm_none__']);
      map.getCanvas().style.cursor = 'default';
      show(f.properties.dm_tip || f.properties.dm_label, e.point.x, e.point.y);
    });
    map.on('mouseleave', layer, () => { map.setFilter(outline, NONE); show(null); });
  }
  return show;
}

// ---------- deck.gl arcs: great circles raised by a height tied to length alone ----------

function arcLayers(deck, t, show) {
  const out = [];
  for (const [name, L] of layersOf()) {
    if (L.kind !== 'flows') continue;
    const f = filesOf(name, L), nodes = data[f.nodes]?.features || [];
    const at = Object.fromEntries(nodes.map(n => [n.properties.dm_key ?? n.id, n.geometry.coordinates]));
    const arcs = (data[f.main]?.features || []).map(l => l.properties).filter(p => at[p.dm_o] && at[p.dm_d])
      .map(p => ({...p, from: at[p.dm_o], to: at[p.dm_d]})).sort((a, b) => a.dm_order - b.dm_order);
    if (!arcs.length) continue;
    const longest = Math.max(...arcs.map(a => a.dm_km || 1));
    const apex = spec.arcs?.apex ?? ARC_APEX;
    // deck.gl's arc peaks at height * length / 2 (arc-layer-vertex.glsl), so this puts the longest flow's apex at
    // APEX of the Earth's radius and every other apex in proportion to its length.
    const height = 2 * apex / (longest / EARTH_KM);
    out.push({name, apex, longest, height, layer: new deck.ArcLayer({
      id: name, data: arcs, greatCircle: true, numSegments: 64,
      // The globe culls back faces and 9.4.1's arc strips wind clockwise, so without this they vanish (deck.gl #10670).
      parameters: {cullMode: 'none'},
      beforeId: data[f.arrows] ? name + '-arrows' : undefined,
      getSourcePosition: a => a.from, getTargetPosition: a => a.to, getHeight: height,
      getWidth: a => a.dm_width, widthUnits: 'pixels',
      getSourceColor: a => rgb(a.dm_fill || L.color || t.flow), getTargetColor: a => rgb(a.dm_fill || L.color || t.flow),
      pickable: true, onHover: info => show(info.object?.dm_tip, info.x, info.y)
    })});
  }
  return out;
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
    zoom: map?.getZoom() ?? null, minZoom: map?.getMinZoom() ?? null, maxZoom: map?.getMaxZoom() ?? null,
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
    rendered: renderedCounts(map),
    viewport: {w: innerWidth, h: innerHeight, dpr: devicePixelRatio}
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
  return out;
}
function angularKm([a, b], [c, d]) {
  const x = Math.sin(b * RAD) * Math.sin(d * RAD) + Math.cos(b * RAD) * Math.cos(d * RAD) * Math.cos((c - a) * RAD);
  return EARTH_KM * Math.acos(Math.min(1, Math.max(-1, x)));
}

function baseColors(style) {
  const ids = new Set((style?.layers || []).map(l => l.id));
  const has = re => [...ids].some(id => re.test(id));
  return [['page', true], ['ocean', !!style], ['graticule', has(/-lines$/)], ['sphere-edge', has(/-edge$/)],
    ['land', ids.has('land')], ['land-edge', ids.has('land-edge')]].filter(([, on]) => on).map(([k]) => tok(k));
}

// A wide projection in a tall cell leaves bands above and below the map; give the map row the map's own
// height and center the figure on the page instead.
function hugMap(map) {
  const cell = $('dm-map-cell'), {clientWidth: w, clientHeight: h} = cell;
  if (spec.projection.type === 'globe' || innerWidth <= 720) return false;
  const e = spec.extent, pts = [];
  const b = e === 'world' ? [-180, -90, 180, 90] : Array.isArray(e) ? e : bbox(thematicPoints()).flat();
  for (let i = 0; i <= 36; i++) {
    const t = i / 36;
    pts.push([b[0] + t * (b[2] - b[0]), b[1]], [b[0] + t * (b[2] - b[0]), b[3]], [b[0], b[1] + t * (b[3] - b[1])], [b[2], b[1] + t * (b[3] - b[1])]);
  }
  const xy = pts.map(p => map.project(p)), xs = xy.map(p => p.x), ys = xy.map(p => p.y);
  const aspect = (Math.max(...xs) - Math.min(...xs)) / (Math.max(...ys) - Math.min(...ys));
  const aside = $('dm-side'), top = aside ? aside.getBoundingClientRect().top : 0;
  const side = aside ? Math.max(0, ...[...aside.querySelectorAll('section')].map(e => e.getBoundingClientRect().bottom - top)) : 0;
  const want = Math.max(Math.ceil(w / aspect) + 28, side);
  if (want >= h - 8) return false;
  document.body.style.height = 'auto';
  document.body.style.minHeight = '100%';
  document.body.style.gridTemplateRows = `auto ${want}px auto`;
  document.body.style.alignContent = 'center';
  map.resize();
  return true;
}

// ---------- start ----------

const once = (target, event) => new Promise(r => target.once(event, r));

async function start(libs, extend) {
  document.body.classList.toggle('dm-chart', !spec.projection);
  drawLegend();
  drawCompanions();
  if (!spec.projection) {
    window.dataMap.report = () => report(null, null);
    await document.fonts.ready;
    resolveReady();
    return;
  }
  const {maplibregl, deck} = libs;
  const proj = spec.projection, crs = proj.type === 'crs';
  if (crs) await registerCrs(maplibregl, libs.proj4, libs.proj4Url, proj);
  if (libs.pmtiles) maplibregl.addProtocol('pmtiles', new libs.pmtiles.Protocol().tile);
  const t = Object.fromEntries(['page', 'ocean', 'graticule', 'sphere-edge', 'land', 'land-edge', 'flow', 'node', 'symbol', 'text'].map(k => [k, tok(k)]));
  const {style, hover} = buildStyle(libs, t);
  const map = new maplibregl.Map({container: 'map', style, attributionControl: {compact: true},
    pitch: spec.pitch || 0, maxPitch: spec.pitch || 0, dragRotate: false, pitchWithRotate: false, touchPitch: false,
    renderWorldCopies: false, fadeDuration: 0});
  map.touchZoomRotate.disableRotation();
  map.keyboard.disableRotation();
  map.setMissingStyleImageResolver(id => {
    const [make, options] = IMAGES[id] || [];
    if (make && !map.hasImage(id)) map.addImage(id, make(), options);
  });
  map.on('error', e => rejectReady(e.error || new Error(String(e))));
  await once(map, 'load');
  fitView(map);
  if (hugMap(map)) fitView(map);
  screenArrows(map);
  // Panning a globe turns every place's north on screen; Mercator and a CRS keep their angles under pan and zoom.
  if (proj.type === 'globe') map.on('move', () => screenArrows(map));
  const show = interact(map, hover);
  let arcs = null, drawn = Promise.resolve(), overlay = null;
  if (deck) {
    let frame;
    drawn = new Promise(r => { frame = r; });
    arcs = arcLayers(deck, t, show);
    overlay = new deck.MapLibreOverlay({interleaved: true, layers: arcs.map(a => a.layer),
      onAfterRender: () => frame(), onError: err => rejectReady(err)});
    map.addControl(overlay);
  }
  if (extend) await extend({map, overlay, data, spec, legend, libs});
  map.triggerRepaint();
  await Promise.all([once(map, 'idle'), drawn]);
  window.dataMap.report = () => report(map, arcs);
  window.dataMap.map = map;
  await document.fonts.ready;
  resolveReady();
}

window.DataMap = {spec, data, legend, start: (libs, extend) => start(libs, extend).catch(err => { rejectReady(err); throw err; })};
})();
