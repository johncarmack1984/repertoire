/* data-dashboard 0.2.0: Stephen Few's dashboard display media, drawn as SVG. MIT license. */
(() => {
'use strict'
const VERSION = '0.2.0'
const POLICY = { warn: 0.95, alert: 0.85 }
const WORD = { good: 'good', ok: 'satisfactory', warn: 'warning', alert: 'critical', none: 'no comparison' }
const DOTC = { warn: 'dd-dot-warn', alert: 'dd-dot-alert' }
const TONES = [[4], [1, 4], [1, 2, 4], [0, 1, 2, 4], [0, 1, 2, 3, 4]]
const END = { 'text-anchor': 'end' }, EDGE = 2
const MID = { 'text-anchor': 'middle' }
const now = { locale: 'en-US', currency: 'USD', policy: POLICY }
const isNum = v => typeof v === 'number' && Number.isFinite(v)
const clamp = (v, a, b) => min(b, max(a, v))
const { round: px, max, min } = Math
const most = (xs, d = 0) => xs.length ? max(...xs) : d
const join = (...xs) => xs.filter(Boolean).join(': ')

class Raw { constructor (s) { this.s = s } toString () { return this.s } }
const esc = s => String(s).replace(/[&<>"']/g, c => '&#' + c.charCodeAt(0) + ';')
function h (tag, attrs, ...kids) {
  let a = ''
  for (const k in attrs) {
    let v = attrs[k]
    if (v == null || v === false) continue
    if (typeof v === 'number') v = px(v * 100) / 100
    a += ` ${k}="${esc(v)}"`
  }
  const body = kids.flat(Infinity).map(k => k == null || k === false ? '' : k instanceof Raw ? k.s : esc(k)).join('')
  return new Raw('<' + tag + a + '>' + body + '</' + tag + '>')
}
const T = (x, y, s, size, cls = 'dd-t', more) => h('text', { x, y, 'font-size': size, class: cls, ...more }, s)
const R = (x, y, w, ht, cls) => h('rect', { x, y, width: max(0, w), height: max(0, ht), class: cls })
const dot = (cx, cy, r, level) => DOTC[level] ? h('circle', { cx, cy, r, class: DOTC[level] + ' dd-mark' }) : null
const LINE = 1.3, DOT = LINE, DOTGAP = 0.4
const alertDot = (cx, cy, fs, level) => dot(cx, cy, fs * DOT / 2, level)
const dotCol = fs => px(fs * (DOT + DOTGAP))
const bold = level => DOTC[level] ? { 'font-weight': 700 } : {}
const row = (level, label, title, kids, key) => h('g', { 'data-dd-level': level, 'data-dd-label': level ? label : null, 'data-dd-key': key }, h('title', {}, title), kids)
const NS = 'http://www.w3.org/2000/svg'
const svg = (W, H, label, kids, cls, style) => String(h('svg', {
  xmlns: NS, width: W, height: H, viewBox: `0 0 ${W} ${H}`,
  role: label == null ? null : 'img', 'aria-label': label, 'aria-hidden': label == null ? 'true' : null, class: 'dd-svg ' + cls, style
}, kids))

const FORMATS = {
  int: { max: 0 },
  dec1: { min: 1, max: 1 },
  usd0: { cur: 1, max: 0 },
  usd0k: { cur: 1, max: 0, div: 1e3, suffix: 'K', say: 'thousand dollars' },
  usd1m: { cur: 1, min: 1, max: 1, div: 1e6, suffix: 'M', say: 'million dollars' },
  pct0: { pct: 1, max: 0 },
  pct1: { pct: 1, min: 1, max: 1 },
  '+pct0': { pct: 1, max: 0, sign: 1 },
  '+pct1': { pct: 1, min: 1, max: 1, sign: 1 }
}
const nfs = new Map()
function spec (s) {
  const f = FORMATS[s || 'int']
  if (!f) throw new Error(`dd.fmt: unknown format "${s}"; use one of ${Object.keys(FORMATS).join(', ')}`)
  return f
}
function number (v, f, digits, currency) {
  const o = {
    style: f.pct ? 'percent' : currency ? 'currency' : 'decimal', currency: now.currency,
    minimumFractionDigits: digits[0], maximumFractionDigits: digits[1], signDisplay: f.sign ? 'exceptZero' : 'auto'
  }
  const key = JSON.stringify([now.locale, o])
  if (!nfs.has(key)) nfs.set(key, new Intl.NumberFormat(now.locale, o))
  return nfs.get(key).format(v / (f.pct ? 1 : f.div || 1)).replace(/-/g, '−')
}
function fmt (v, s, bare) {
  if (!isNum(v)) return '–'
  const f = spec(s)
  return number(v, f, [f.min || 0, f.max], f.cur && !bare) + (bare ? '' : f.suffix || '')
}
const say = (v, s) => spec(s).say && isNum(v) ? `${fmt(v, s, true)} ${spec(s).say}` : fmt(v, s)
function tick (v, s, step) {
  const f = spec(s), d = step / (f.pct ? 0.01 : f.div || 1)
  let n = 0
  while (n < 3 && Math.abs(d * 10 ** n - px(d * 10 ** n)) > 1e-6) n++
  return number(v, f, [n, n], false)
}

function asOf (iso, tz, locale) {
  if (!iso) return ''
  const d = new Date(iso), loc = locale || now.locale
  if (isNaN(d)) return String(iso)
  const o = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
  if (tz) return new Intl.DateTimeFormat(loc, { ...o, timeZone: tz, timeZoneName: 'short' }).format(d)
  const m = /(?:([+-])(\d\d):?(\d\d)|Z)$/.exec(iso)
  if (!m) return new Intl.DateTimeFormat(loc, { ...o, timeZoneName: 'short' }).format(d)
  const off = m[1] ? (m[1] === '-' ? -1 : 1) * (60 * m[2] + +m[3]) : 0
  const wall = new Intl.DateTimeFormat(loc, { ...o, timeZone: 'UTC' }).format(new Date(+d + off * 6e4))
  return `${wall} ${off ? `UTC${m[1] === '-' ? '−' : '+'}${m[2]}:${m[3]}` : 'UTC'}`
}

function basis (m) {
  for (const kind of ['target', 'forecast', 'prior']) if (isNum(m[kind]) && m[kind] !== 0) return { kind, value: m[kind] }
  return null
}
const pol = (m, policy) => ({ ...POLICY, ...(policy || now.policy), ...m.policy })
const goodness = (r, better) => better === 'down' ? 2 - r : r
const ladder = (g, p) => g >= 1 ? 'good' : g < p.alert ? 'alert' : isNum(p.warn) && g < p.warn ? 'warn' : 'ok'
function breaks (m, policy) {
  if (Array.isArray(m.ranges) && m.ranges.length) return m.ranges
  const b = basis(m), p = pol(m, policy)
  if (!b || m.better === 'in') return null
  return [p.alert, p.warn].filter(isNum).map(x => b.value * goodness(x, m.better))
}

function state (m, policy) {
  const p = pol(m, policy), b = basis(m), proj = isNum(m.projection)
  const v = proj ? m.projection : m.value
  const ratio = b && isNum(v) ? v / b.value : null
  let level = m.state
  if (level != null && !WORD[level]) throw new Error(`dd.state: ${m.label} has state "${level}"; use good, ok, warn or alert`)
  if (level == null) {
    if (!isNum(v)) level = 'none'
    else if (m.better === 'in' && Array.isArray(m.norm)) {
      const [lo, hi] = m.norm
      level = ladder(v < lo ? v / lo : v > hi ? 2 - v / hi : 1, p)
    } else if (Array.isArray(m.ranges) && m.ranges.length) {
      const n = m.ranges.length + 1
      const i = m.ranges.filter(x => m.better === 'down' ? v <= x : v >= x).length
      level = i === 0 ? 'alert' : i === 1 && n > 2 && isNum(p.warn) ? 'warn' : i === n - 1 ? 'good' : 'ok'
    } else level = ratio == null ? 'none' : ladder(goodness(ratio, m.better), p)
  }
  const cmp = m.better === 'in' && Array.isArray(m.norm) ? `normal range ${fmt(m.norm[0], m.format)} to ${fmt(m.norm[1], m.format)}`
    : !b || !isNum(v) ? '' : b.kind === 'prior' ? `${fmt(ratio - 1, '+pct1')} vs. prior`
      : `${proj ? 'projected ' : ''}${fmt(ratio, 'pct0')} of ${b.kind}`
  const text = [`${m.label ?? ''} ${say(m.value, m.format)}`.trim(), cmp, m.note, WORD[level]].filter(Boolean).join(', ')
  return { level, ratio, text }
}

const norm = (m, key) => ({ key, better: 'up', format: 'int', ...m, label: m.label ?? key ?? '' })
function pick (input, keys) {
  if (!keys) return (Array.isArray(input) ? input : Object.values(input || {})).map(m => norm(m, m.key))
  return keys.map(k => {
    if (!input || !input[k]) throw new Error(`dd: no measure "${k}" in the data`)
    return norm(input[k], k)
  })
}
function data (sel = '#dd-data') {
  const el = document.querySelector(sel)
  if (!el) throw new Error(`dd.data: no ${sel} element; add <script type="application/json" id="dd-data">`)
  const d = JSON.parse(el.textContent.trim() || '{}')
  now.locale = d.locale = d.locale || 'en-US'
  now.currency = d.currency || 'USD'
  now.policy = d.policy = { ...POLICY, ...d.policy }
  const ms = d.measures = d.measures || {}
  for (const k of Object.keys(ms)) {
    ms[k] = norm(ms[k], Array.isArray(ms) ? ms[k].key : k)
    ms[k].status = state(ms[k], d.policy)
  }
  return d
}

const estimate = (t, size, weight) => String(t).length * size * (weight > 500 ? 0.6 : 0.55)
let probe
const measurer = font => (t, size, weight = 400) => {
  if (!probe) {
    const s = document.body.appendChild(document.createElementNS(NS, 'svg'))
    s.setAttribute('class', 'dd-sr')
    s.setAttribute('aria-hidden', 'true')
    probe = s.appendChild(document.createElementNS(NS, 'text'))
  }
  probe.setAttribute('style', `font: ${weight} ${size}px ${font}; font-variant-numeric: tabular-nums`)
  probe.textContent = String(t)
  return probe.getComputedTextLength()
}
function env (o) {
  const u = o.u || 20, fs = px(u * 1.25) / 2
  return {
    u, fs, sm: max(9, px(fs * 1.6) / 2), W: max(60, Math.floor(o.width || 400)),
    tw: o.measure || estimate, policy: o.policy, gap: px(fs * 0.8)
  }
}
function clip (t, w, size, weight, tw) {
  t = String(t ?? '')
  if (tw(t, size, weight) <= w) return t
  let lo = 0, hi = t.length
  while (lo < hi) {
    const m = (lo + hi + 1) >> 1
    if (tw(t.slice(0, m) + '…', size, weight) <= w) lo = m; else hi = m - 1
  }
  return t.slice(0, lo).trimEnd() + '…'
}
const mid = size => size * 0.35

function lin (d0, d1, r0, r1) {
  const f = v => r0 + (v - d0) / ((d1 - d0) || 1) * (r1 - r0)
  f.d = [d0, d1]
  return f
}
function nice (lo, hi, n = 5) {
  if (!(hi > lo)) hi = lo + (Math.abs(lo) || 1)
  const raw = (hi - lo) / n, p = 10 ** Math.floor(Math.log10(raw)), r = raw / p
  const step = (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * p
  const ticks = []
  for (let t = Math.floor(lo / step + 1e-9) * step; t <= Math.ceil(hi / step - 1e-9) * step + step / 2; t += step) {
    ticks.push(+(px(t / step) * step).toPrecision(12))
  }
  return { lo: ticks[0], hi: ticks[ticks.length - 1], step, ticks }
}
function fixed ([lo, hi], n) {
  const t = nice(lo, hi, n)
  return { ...t, lo, hi, ticks: t.ticks.filter(v => v >= lo - 1e-9 && v <= hi + 1e-9) }
}
function scaleFor (lo, hi, span, f, e, exact, vertical) {
  let best = null
  for (let n = 1; n <= 7; n++) {
    const t = exact ? fixed([lo, hi], n) : nice(lo, hi, n)
    const room = vertical ? e.sm * 1.6 : most(t.ticks.map(v => e.tw(tick(v, f, t.step), e.sm))) + e.sm
    const fits = t.ticks.length < 2 || room <= span * t.step / (t.hi - t.lo)
    if (fits && t.ticks.length <= 7 && (!best || t.hi - t.lo < best.hi - best.lo - 1e-9 || (t.hi - t.lo <= best.hi - best.lo + 1e-9 && t.ticks.length > best.ticks.length))) best = t
  }
  return best || (exact ? fixed([lo, hi], 1) : nice(lo, hi, 1))
}
function axisX (sc, t, y, f, e, line = true, len = px(e.fs * 0.35)) {
  const [x0, x1] = sc.d.map(v => px(sc(v)))
  return [line ? R(x0, y, x1 - x0 + 1, 1, 'dd-axis') : null, t.ticks.map(v => {
    const x = px(sc(v)), s = tick(v, f, t.step), w = e.tw(s, e.sm) / 2
    const anchor = x - w < 0 ? 'start' : x + w > e.W ? 'end' : 'middle'
    return [R(x, y, 1, len, 'dd-axis'), T(anchor === 'start' ? 0 : anchor === 'end' ? e.W : x + 0.5, y + len + e.sm, s, e.sm, 'dd-t3', { 'text-anchor': anchor })]
  })]
}
const axisH = e => px(e.fs * 0.35) + e.sm + 6
const yWidth = (t, f, e) => Math.ceil(most(t.ticks.map(v => e.tw(tick(v, f, t.step), e.sm)))) + 8
const axisY = (sy, t, x0, y0, y1, f, e) => [R(x0, y0, 1, y1 - y0 + 1, 'dd-axis'),
  t.ticks.map(v => [R(x0 - 4, px(sy(v)), 4, 1, 'dd-axis'), T(x0 - 6, px(sy(v)) + mid(e.sm), tick(v, f, t.step), e.sm, 'dd-t3', END)])]

function bandsOf (m, policy, d0, d1) {
  if (m.better === 'in' && Array.isArray(m.norm)) return [[d0, m.norm[0], 1], [m.norm[0], m.norm[1], 4], [m.norm[1], d1, 1]]
  const br = breaks(m, policy)
  if (!br) return []
  const edges = m.better === 'down' ? [d1, ...br, d0] : [d0, ...br, d1]
  return TONES[min(br.length, 4)].map((t, i) => [edges[i], edges[i + 1], t])
}
function bulletMarks (m, policy, sc, y, b, fs, target = true) {
  const [d0, d1] = sc.d, out = [], X = v => px(sc(clamp(v, d0, d1)))
  for (const [a, c, t] of bandsOf(m, policy, d0, d1)) {
    const x0 = X(min(a, c)), x1 = X(max(a, c))
    if (x1 > x0) out.push(R(x0, y, x1 - x0, b, 'dd-band dd-band-' + t))
  }
  const bh = max(3, px(b / 3)), by = y + px((b - bh) / 2), v = m.value, zero = d0 <= 0 && d1 >= 0
  if (isNum(v) && zero) {
    const z = X(0), x = X(v), top = max(v, isNum(m.projection) ? m.projection : v)
    out.push(R(min(z, x), by, Math.abs(x - z), bh, 'dd-bar dd-mark dd-crisp'))
    if (top > v) out.push(R(x, by, X(top) - x, bh, 'dd-proj dd-crisp'))
    if (top > d1) out.push(R(X(d1) - 5, by - 1, 2, bh + 2, 'dd-break dd-crisp'))
    if (v < d0) out.push(R(X(d0) + 3, by - 1, 2, bh + 2, 'dd-break dd-crisp'))
  } else if (isNum(v)) {
    out.push(h('circle', { cx: sc(clamp(v, d0, d1)), cy: y + b / 2, r: max(bh, fs * 0.5) / 2, class: 'dd-bar dd-mark' }))
  }
  if (target && isNum(m.target) && m.target >= d0 && m.target <= d1) {
    const w = zero ? max(2, px(bh / 3)) : 1, th = px(b * 0.7)
    out.push(R(px(sc(m.target) - w / 2), y + px((b - th) / 2), w, th, 'dd-tgt dd-mark dd-crisp'))
  }
  return out
}
function ownScale (m, span, e) {
  if (Array.isArray(m.domain)) return scaleFor(m.domain[0], m.domain[1], span, m.format, e, true)
  const xs = [m.value, m.target, m.projection, m.forecast, m.prior, ...(m.ranges || []), ...(m.norm || [])].filter(isNum)
  return scaleFor(min(0, ...xs), most(xs, 1) * 1.05, span, m.format, e)
}

function sparkMarks (m, st, x, y, w, ht, o = {}) {
  const hs = (m.history || []).filter(isNum)
  if (!hs.length) return []
  const band = o.norm !== false && Array.isArray(m.norm) ? m.norm : null
  let lo = min(...hs), hi = max(...hs)
  if (hi === lo) { lo -= 1; hi += 1 }
  const pad = 2.5, sy = lin(lo, hi, y + ht - pad, y + pad), Y = v => v <= lo ? y + ht : v >= hi ? y : px(sy(v))
  const sx = i => hs.length === 1 ? x + w - pad : x + pad + i * (w - 2 * pad) / (hs.length - 1)
  const leaves = band && hs.some(v => v < band[0] || v > band[1])
  const out = leaves && Y(band[0]) > Y(band[1]) ? [R(x, Y(band[1]), w, Y(band[0]) - Y(band[1]), 'dd-norm dd-crisp')] : []
  if (hs.length > 1) out.push(h('path', { d: 'M' + hs.map((v, i) => `${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join('L'), class: 'dd-spark dd-mark' }))
  const end = [sx(hs.length - 1), sy(hs[hs.length - 1])], flag = o.endDot === 'always' || (o.endDot !== 'none' && DOTC[st.level])
  if (flag && DOTC[st.level]) out.push(dot(...end, 2.5, st.level))
  else if (flag || hs.length === 1) out.push(h('circle', { cx: end[0], cy: end[1], r: 2, class: 'dd-pt dd-mark' }))
  return out
}

const SCALES = ['pctTarget', 'shared', 'own']
function table (input, o) {
  const e = env(o), { fs, sm, W, tw, gap } = e, mode = o.scale || 'pctTarget'
  if (!SCALES.includes(mode)) throw new Error(`dd.table: scale "${mode}" is unknown; use ${SCALES.join(', ')}`)
  const rows = pick(input, o.rows), cols = new Set(o.cols || ['spark', 'alert', 'label', 'graph', 'value'])
  const head = o.head, hw = k => head && head[k] ? tw(head[k], sm) : 0, len = v => typeof v === 'string' ? parseFloat(v) : v * e.u
  const pct = mode === 'pctTarget', units = rows.some(m => m.units), lh = px(fs * LINE)
  const sts = rows.map(m => state(m, e.policy)), vals = rows.map(m => fmt(m.value, m.format))
  const sw = cols.has('spark') ? clamp(px(W * 0.26), 7 * lh, 10 * lh) : 0
  const dw = cols.has('alert') ? dotCol(fs) : 0
  const vw = cols.has('value') ? Math.ceil(most([...vals.map(t => tw(t, fs, 700)), hw('value'), o.valueWidth ? len(o.valueWidth) : 0])) : 0
  const lw = !cols.has('label') ? 0 : o.labelWidth ? px(len(o.labelWidth))
    : Math.ceil(clamp(most([...rows.map(m => max(tw(m.label, fs), m.units ? tw(m.units, sm) : 0)), hw('label')]), 4 * fs, W * 0.24))
  const xl = (sw ? max(sw, hw('spark')) + gap : 0) + dw, gx0 = xl + (lw ? lw + gap : 0), gx1 = W - (vw ? vw + gap : 0)
  const b = px(fs * 1.04), tk = px(fs * 0.35), graph = cols.has('graph') && gx1 - gx0 > fs * 3, own = mode === 'own' && graph
  const asc = px(fs * 1.05), text = asc + (units ? px(sm * LINE) : 0) + px(fs * 0.3)
  const pitch = max(px(fs * (units ? 2.3 : 1.8)), own ? max(text, b + tk + sm + 4) + px(fs * 0.6) : 0)
  const ruleY = head ? px(sm * 1.45) : 0, top = head ? ruleY + px(fs * 0.35) : 0
  const ratio = m => {
    const bs = basis(m)
    if (!bs) return null
    const k = bs.value, div = a => a && a.map(x => x / k)
    return { ...m, target: undefined, forecast: undefined, prior: undefined, [bs.kind]: 1, value: m.value / k, projection: isNum(m.projection) ? m.projection / k : undefined, ranges: div(m.ranges), norm: div(m.norm) }
  }
  const rs = pct ? rows.map(ratio) : mode === 'shared' ? rows : [], f = pct ? 'pct0' : rows.length ? rows[0].format : 'int'
  const xs = rs.filter(Boolean).flatMap(r => [r.value, r.projection, r.target, r.forecast, r.prior]).filter(isNum)
  const line = pct ? 1 : rows.length && rows.every(m => isNum(m.target) && m.target === rows[0].target) ? rows[0].target : null
  const foot = rs.length && graph ? (o.domain ? scaleFor(o.domain[0], o.domain[1], gx1 - gx0, f, e, true) : scaleFor(min(0, ...xs), pct ? max(1.5, ...xs) : most(xs, 1) * 1.05, gx1 - gx0, f, e)) : null
  const sc = foot && lin(foot.lo, foot.hi, gx0, gx1)
  const kids = []
  if (head) {
    const hy = ruleY - px(sm * 0.4)
    kids.push(R(0, ruleY, W, 1, 'dd-rule'), head.spark && sw ? T(0, hy, head.spark, sm, 'dd-t3') : null,
      head.label && lw ? T(xl, hy, clip(head.label, lw, sm, 400, tw), sm, 'dd-t3') : null, head.graph && graph ? T(gx0, hy, clip(head.graph, W - hw('value') - gap - gx0, sm, 400, tw), sm, 'dd-t3') : null,
      head.value && vw ? T(W - EDGE, hy, head.value, sm, 'dd-t3', END) : null)
  }
  rows.forEach((m, i) => {
    const st = sts[i], y0 = top + i * pitch
    const by = own ? y0 + asc - px(mid(fs) + b / 2) : px(y0 + (pitch - b) / 2)
    const cy = by + b / 2, lb = own ? y0 + asc : m.units ? cy - px(fs * 0.12) : cy + mid(fs), g = []
    if (sw) g.push(sparkMarks(m, st, 0, px(cy - lh / 2), sw, lh, o))
    if (dw) g.push(alertDot(xl - fs * (DOTGAP + DOT / 2), cy, fs, st.level))
    if (lw) g.push(T(xl, lb, clip(m.label, lw, fs, 400, tw), fs), m.units ? T(xl, lb + px(sm * LINE), clip(m.units, lw, sm, 400, tw), sm, 'dd-t2') : null)
    if (rs[i] && sc) g.push(bulletMarks(rs[i], e.policy, sc, by, b, fs, line == null))
    if (own) {
      const t = ownScale(m, gx1 - gx0, e), s = lin(t.lo, t.hi, gx0, gx1)
      g.push(bulletMarks(m, e.policy, s, by, b, fs), axisX(s, t, by + b, m.format, { ...e, W: gx1 }, false))
    }
    if (vw) g.push(T(W - EDGE, cy + mid(fs), vals[i], fs, 'dd-t', { ...END, ...bold(st.level) }))
    const extra = [isNum(m.target) && `target ${fmt(m.target, m.format)}`, isNum(m.projection) && `projection ${fmt(m.projection, m.format)}`]
    kids.push(row(st.level, m.label, [st.text, ...extra].filter(Boolean).join('; '), g, m.key))
  })
  let H = top + rows.length * pitch
  if (sc) {
    const ay = H + 3, y = top + px((pitch - b) / 2) - 3
    if (line != null && foot.lo <= line && foot.hi >= line) kids.push(R(px(sc(line)) - 1, y, 2, ay - y, 'dd-tgt dd-mark dd-crisp'))
    if (o.axis !== false) { kids.push(axisX(sc, foot, ay, f, e)); H = ay + axisH(e) }
  }
  return svg(W, H, join(o.title, sts.map(s => s.text).join('; ')), kids, 'dd-table')
}

function bullet (input, o) {
  const e = env(o), { fs, sm, W, tw, gap } = e
  const ms = (Array.isArray(input) ? input : [input]).map(m => norm(m, m.key)), sts = ms.map(m => state(m, e.policy))
  const b = px(e.u * 1.4), tk = px(b * 0.22), pitch = px(b * 2.35), lg = px(b * 0.45)
  const vals = ms.map(m => fmt(m.value, m.format)), dw = dotCol(fs)
  const lw = Math.ceil(clamp(most(ms.map(m => max(tw(m.label, fs, 600), m.units ? tw(m.units, sm) : 0))), 3 * fs, W * 0.35))
  const vw = o.value === false ? 0 : Math.ceil(most(vals.map(t => tw(t, fs, 700)))) + gap
  const x0 = dw + lw + lg, x1 = min(W - vw - px(fs), x0 + 13 * b), right = x1 + px(fs) + vw
  const kids = ms.map((m, i) => {
    const st = sts[i], y = i * pitch + 1, cy = y + b / 2, t = ownScale({ ...m, domain: m.domain || o.domain }, x1 - x0, e)
    const sc = lin(t.lo, t.hi, x0, x1)
    return row(st.level, m.label, st.text, [alertDot(fs * DOT / 2, cy, fs, st.level),
      T(x0 - lg, m.units ? cy - px(fs * 0.1) : cy + mid(fs), clip(m.label, lw, fs, 600, tw), fs, 'dd-t', { ...END, 'font-weight': 600 }),
      m.units ? T(x0 - lg, cy + px(sm * 1.2), clip(m.units, lw, sm, 400, tw), sm, 'dd-t2', END) : null,
      bulletMarks(m, e.policy, sc, y, b, fs), axisX(sc, t, y + b, m.format, { ...e, W: x1 + fs }, false, tk),
      vw ? T(right - EDGE, cy + mid(fs), vals[i], fs, 'dd-t', { ...END, ...bold(st.level) }) : null], m.key)
  })
  return svg(right, (ms.length - 1) * pitch + b + tk + sm + 6, sts.map(s => s.text).join('; '), kids, 'dd-bullet')
}

function spark (input, o) {
  const e = env(o), { fs, gap } = e, m = norm(input, input.key), st = state(m, e.policy), ht = px(fs * LINE)
  const val = fmt(m.value, m.format), vw = e.tw(val, fs, 700), text = o.text !== false
  const tw = text ? vw + gap + e.tw(m.label, fs) : 0
  const w = px(clamp(e.W - (text ? tw + gap : 0), ht * 4, ht * 10)), y = ht / 2 + mid(fs)
  return svg(Math.ceil(text ? w + gap + tw : w), ht, st.text, row(st.level, m.label, st.text, [sparkMarks(m, st, 0, 0, w, ht, o),
    text ? [T(w + gap, y, val, fs, 'dd-t', { 'font-weight': 700 }), T(w + gap * 2 + vw, y, m.label, fs, 'dd-t2')] : null], m.key), 'dd-spark-svg')
}

function frame (e, labels, cols, dots, top = 0) {
  const { fs, W, tw, gap } = e, slot = px(fs * 1.8), dw = dots ? dotCol(fs) : 0
  const lw = Math.ceil(clamp(most(labels.map(l => tw(l, fs, 600))), 2 * fs, W * 0.34))
  const cw = cols.map(c => Math.ceil(most(c.map(t => tw(t, fs, 700)))))
  const x0 = dw + lw + gap, x1 = W - cw.reduce((a, w) => a + w + gap, 0) - px(fs * 0.6)
  const ends = cw.map((w, k) => x1 + px(fs * 0.6) + cw.slice(0, k + 1).reduce((a, c) => a + c + gap, 0))
  const cy = i => top + i * slot + slot / 2
  const cells = (i, level, hi) => [dw ? alertDot(fs * DOT / 2, cy(i), fs, level) : null,
    T(dw, cy(i) + mid(fs), clip(labels[i], lw, fs, hi ? 600 : 400, tw), fs, 'dd-t', { 'font-weight': hi ? 600 : null }),
    cols.map((c, k) => T(ends[k] - EDGE, cy(i) + mid(fs), c[i], fs, k ? 'dd-t2' : 'dd-t', { ...END, ...(k ? {} : bold(level)) }))]
  return { x0, x1, slot, cy, cells, H: top + labels.length * slot }
}
function sortRows (rows, how) {
  const others = r => r.others || /^all others?$/i.test(r.label)
  const list = how === 'none' ? rows.slice() : rows.slice().sort((a, b) => how === 'asc' ? a.value - b.value : b.value - a.value)
  return list.filter(r => !others(r)).concat(list.filter(others))
}
function barRows (rows, o, sortDefault) {
  const hi = r => typeof o.highlight === 'function' ? !!o.highlight(r) : o.highlight != null ? r.label === o.highlight : !!r.highlight
  return sortRows(rows.map(r => norm({ format: o.format || 'int', ...r }, r.key)), o.sort || sortDefault)
    .map(r => ({ ...r, hi: hi(r), st: basis(r) || r.state ? state(r, o.policy) : null }))
}
function zeroScale (o, xs, span, f, e, vertical) {
  if (!o.domain) return scaleFor(min(0, ...xs) * 1.04, max(0, ...xs) * 1.04, span, f, e, true, vertical)
  if (o.domain[0] > 0 || o.domain[1] < 0) throw new Error('dd: bars start at zero (mistake 8); give a domain that includes 0, or use dd.bullet, which draws a marker on a scale that does not')
  return scaleFor(o.domain[0], o.domain[1], span, f, e, true, vertical)
}
const level = r => r.st ? r.st.level : null
function bars (input, o) {
  if (o.orient === 'v') return barsV(input, o)
  const e = env(o), { fs } = e, rows = barRows(input, o, 'desc'), f = o.format || 'int'
  const total = rows.reduce((s, r) => s + (r.value > 0 ? r.value : 0), 0)
  const vals = rows.map(r => fmt(r.value, f)), pcts = o.pctTotal ? rows.map(r => fmt(r.value / total, 'pct0')) : null
  const F = frame(e, rows.map(r => r.label), [o.values === false ? null : vals, pcts].filter(Boolean), rows.some(r => r.st))
  const t = zeroScale(o, rows.flatMap(r => [r.value, r.target]).filter(isNum), F.x1 - F.x0, f, e)
  const sc = lin(t.lo, t.hi, F.x0, F.x1), X = v => px(sc(clamp(v, t.lo, t.hi))), z = X(0), bh = px(F.slot * 0.56)
  const kids = rows.map((r, i) => {
    const cy = F.cy(i), by = px(cy - bh / 2), x = X(r.value)
    return row(level(r), r.label, r.st ? r.st.text : `${r.label} ${vals[i]}${pcts ? `, ${pcts[i]} of total` : ''}`, [F.cells(i, level(r), r.hi),
      isNum(r.value) ? R(min(z, x), by, Math.abs(x - z), bh, (r.hi ? 'dd-fill-hi' : 'dd-fill') + ' dd-mark dd-crisp') : null,
      isNum(r.target) ? R(X(r.target) - 1, px(cy - bh * 0.8), 2, px(bh * 1.6), 'dd-tgt dd-mark dd-crisp') : null], r.key)
  })
  kids.push(R(z, 0, 1, F.H, t.lo < 0 ? 'dd-zero dd-crisp' : 'dd-axis'))
  if (o.axis !== false) kids.push(axisX(sc, t, F.H + 2, f, e))
  return svg(e.W, F.H + (o.axis !== false ? axisH(e) + 2 : 0), join(o.title, rows.map((r, i) => r.st ? r.st.text : `${r.label} ${vals[i]}`).join('; ')), kids, 'dd-bars')
}
function barsV (input, o) {
  const e = env(o), { fs, sm, W, tw } = e, rows = barRows(input, o, 'none'), f = o.format || 'int'
  const H = px((o.height || 8) * e.u), vals = rows.map(r => fmt(r.value, f))
  const dh = rows.some(r => r.st) ? px(fs * DOT) + 2 : 0
  const y0 = dh + px(sm * 1.6), y1 = H - px(sm * (rows.some(r => r.value < 0) ? 3.2 : 1.8))
  const t = zeroScale(o, rows.flatMap(r => [r.value, r.target]).filter(isNum), y1 - y0, f, e, true), x0 = yWidth(t, f, e)
  const sy = lin(t.lo, t.hi, y1, y0), Y = v => px(sy(clamp(v, t.lo, t.hi))), zy = Y(0)
  const slot = (W - 2 - x0) / max(1, rows.length), bw = max(2, px(slot * 0.56))
  const kids = [axisY(sy, t, x0 - 1, y0, y1, f, e)]
  rows.forEach((r, i) => {
    const cx = x0 + slot * (i + 0.5), y = Y(r.value), lv = level(r)
    kids.push(row(lv, r.label, r.st ? r.st.text : `${r.label} ${vals[i]}`, [
      isNum(r.value) ? R(px(cx - bw / 2), min(y, zy), bw, Math.abs(zy - y), (r.hi ? 'dd-fill-hi' : 'dd-fill') + ' dd-mark dd-crisp') : null,
      isNum(r.target) ? R(px(cx - bw * 0.8), Y(r.target) - 1, px(bw * 1.6), 2, 'dd-tgt dd-mark dd-crisp') : null,
      T(cx, r.value < 0 ? y + sm + 2 : min(y, zy) - 4, vals[i], sm, 'dd-t2', { ...MID, ...bold(lv) }),
      T(cx, H - 4, clip(r.label, slot - 2, sm, 400, tw), sm, 'dd-t3', MID), alertDot(cx, fs * DOT / 2 + 1, fs, lv)], r.key))
  })
  kids.push(R(x0, zy, W - 2 - x0, 1, t.lo < 0 ? 'dd-zero dd-crisp' : 'dd-axis'))
  return svg(W, H, join(o.title, rows.map((r, i) => `${r.label} ${vals[i]}`).join('; ')), kids, 'dd-bars')
}

function stacked (input, o) {
  const e = env(o), { fs, sm, tw, gap } = e, parts = o.parts || ['actual', 'pipeline'], tk = o.target || 'target', f = o.format || 'int'
  if (parts.length > 3) throw new Error('dd.stacked: at most three parts; fold the rest into one')
  if (o.alertWhen && o.alertWhen !== 'sumBelowTarget') throw new Error(`dd.stacked: alertWhen "${o.alertWhen}" is unknown; use "sumBelowTarget"`)
  const names = o.names || parts.map(k => k[0].toUpperCase() + k.slice(1))
  const rows = input.map(r => {
    const vs = parts.map(k => isNum(r[k]) ? max(0, r[k]) : 0), sum = vs.reduce((a, b) => a + b, 0), short = isNum(r[tk]) && sum < r[tk]
    const m = norm({ label: r.label, value: sum, target: r[tk], format: f, note: o.alertWhen && short ? 'short even if all closes' : null })
    if (o.alertWhen) m.state = short ? 'alert' : 'good'
    return { r, vs, st: state(m, e.policy), shown: fmt(o.value === 'sum' ? sum : vs[0], f), sum }
  })
  const top = px(sm * 1.9), F = frame(e, rows.map(x => x.r.label), [rows.map(x => x.shown)], true, top)
  const t = scaleFor(0, most(rows.flatMap(x => [x.sum, x.r[tk]]).filter(isNum), 1) * 1.04, F.x1 - F.x0, f, e, true)
  const sc = lin(t.lo, t.hi, F.x0, F.x1), bh = px(F.slot * 0.56), s = px(sm * 0.75), kids = []
  let kx = F.x0
  names.concat(rows.some(x => isNum(x.r[tk])) ? ['Target'] : []).forEach((n, i) => {
    kids.push(i < parts.length ? R(kx, sm * 1.2 - s, s, s, `dd-part-${i}`) : R(kx + 2, sm * 1.2 - s - 1, 2, s + 2, 'dd-tgt'), T(kx + s + 4, sm * 1.2, n, sm, 'dd-t2'))
    kx += s + 4 + tw(n, sm) + gap
  })
  rows.forEach((x, i) => {
    const cy = F.cy(i), by = px(cy - bh / 2)
    let acc = 0
    const segs = x.vs.map((v, k) => { const a = px(sc(acc)); acc += v; return R(a, by, px(sc(acc)) - a, bh, `dd-part-${k} dd-mark dd-crisp`) })
    kids.push(row(x.st.level, x.r.label, `${x.st.text}; ${names.map((n, j) => `${n} ${fmt(x.vs[j], f)}`).join(', ')}`, [F.cells(i, x.st.level), segs,
      isNum(x.r[tk]) ? R(px(sc(x.r[tk])) - 1, px(cy - bh * 0.8), 2, px(bh * 1.6), 'dd-tgt dd-mark dd-crisp') : null], x.r.key))
  })
  kids.push(R(px(sc(0)), top, 1, F.H - top, 'dd-axis'))
  if (o.axis !== false) kids.push(axisX(sc, t, F.H + 2, f, e))
  return svg(e.W, F.H + (o.axis !== false ? axisH(e) + 2 : 0), rows.map(x => x.st.text).join('; '), kids, 'dd-stacked')
}

function spread (ys, gap, lo, hi) {
  const o = ys.map((y, i) => ({ y, i })).sort((a, b) => a.y - b.y)
  for (let k = 1; k < o.length; k++) o[k].y = max(o[k].y, o[k - 1].y + gap)
  for (let k = o.length - 1; k >= 0; k--) o[k].y = max(lo, min(o[k].y, k === o.length - 1 ? hi : o[k + 1].y - gap))
  return o.sort((a, b) => a.i - b.i).map(a => a.y)
}
function line (input, o) {
  const e = env(o), { fs, sm, W, tw } = e, X = input.x || [], S = (input.series || []).slice(0, 3)
  const H = px((o.height || 7) * e.u), dev = !!o.deviation, f = o.format || (dev ? '+pct0' : 'int')
  const n = max(X.length, most(S.map(s => s.values.length)))
  const all = S.flatMap(s => s.values).filter(isNum).concat(dev ? [0] : [])
  const y0 = px(sm * 0.8), y1 = H - px(sm * 1.9)
  const t = scaleFor(...(o.domain || [min(...all), max(...all)]), y1 - y0, f, e, !!o.domain, true)
  const ends = S.map(s => s.name || '').concat(dev ? [o.refLabel || 'Target'] : [])
  const x0 = yWidth(t, f, e), x1 = W - (o.endLabels === false ? 4 : Math.ceil(most(ends.map(s => tw(s, sm)))) + 8)
  const sx = i => x0 + (n < 2 ? (x1 - x0) / 2 : i * (x1 - x0) / (n - 1)), sy = lin(t.lo, t.hi, y1, y0)
  const kids = [dev && t.lo < 0 ? R(x0, px(sy(0)), x1 - x0, px(sy(t.lo)) - px(sy(0)), 'dd-tint dd-crisp') : null,
    axisY(sy, t, x0, y0, y1, f, e), R(x0, y1, x1 - x0 + 1, 1, 'dd-axis'), dev ? R(x0, px(sy(0)), x1 - x0, 1, 'dd-zero dd-crisp') : null]
  const lw = most(X.map(x => tw(x, sm))) + sm, every = max(1, Math.ceil(n / max(1, Math.floor((x1 - x0) / lw))))
  X.forEach((x, i) => {
    if (i % every && (i !== n - 1 || sx(i) - sx(i - (i % every)) < lw)) return
    kids.push(R(px(sx(i)), y1, 1, 4, 'dd-axis'), T(sx(i), y1 + 5 + sm, x, sm, 'dd-t3', i === 0 && sx(i) < lw / 2 ? {} : MID))
  })
  const lastY = S.map((s, k) => {
    let d = '', pen = false
    s.values.forEach((v, i) => { if (isNum(v)) { d += `${pen ? 'L' : 'M'}${sx(i).toFixed(1)},${sy(v).toFixed(1)}`; pen = true } else pen = false })
    kids.push(h('path', { d, class: `dd-line dd-line-${s.emphasis ?? k} dd-mark` }), s.values.map((v, i) => isNum(v)
      ? h('circle', { cx: sx(i), cy: sy(v), r: 4, class: 'dd-hit' }, h('title', {}, `${s.name || ''} ${X[i] ?? i}: ${fmt(v, f)}`.trim())) : null))
    const li = s.values.map(isNum).lastIndexOf(true)
    return li < 0 ? y1 : sy(s.values[li])
  })
  if (o.endLabels !== false) {
    spread(dev ? lastY.concat(sy(0)) : lastY, sm * 1.15, y0 + sm * 0.4, y1).forEach((y, k) => kids.push(T(x1 + 6, y + mid(sm), ends[k], sm, k < S.length ? 'dd-t2' : 'dd-t3')))
  }
  const desc = S.map(s => { const v = s.values.filter(isNum); return `${s.name || 'series'} from ${fmt(v[0], f)} to ${fmt(v[v.length - 1], f)}` })
  return svg(W, H, join(o.title, desc.join('; ')), kids, 'dd-line-svg')
}

function quartiles (vs) {
  const s = vs.filter(isNum).sort((a, b) => a - b)
  const q = p => { const i = (s.length - 1) * p, a = Math.floor(i); return s[a] + (s[Math.ceil(i)] - s[a]) * (i - a) }
  return { min: s[0], q1: q(0.25), median: q(0.5), q3: q(0.75), max: s[s.length - 1] }
}
function box (input, o) {
  const e = env(o), f = o.format || 'int', gs = input.map(g => ({ ...g, ...(g.values ? quartiles(g.values) : {}), band: g.band || o.band }))
  const F = frame(e, gs.map(g => g.label), [], false), bh = px(F.slot * 0.5)
  const xs = gs.flatMap(g => [g.min, g.max, ...(g.band || [])]).filter(isNum)
  const t = scaleFor(...(o.domain || [min(0, ...xs), most(xs, 1) * 1.04]), F.x1 - F.x0, f, e, true)
  const sc = lin(t.lo, t.hi, F.x0, F.x1), X = v => px(sc(clamp(v, t.lo, t.hi)))
  const kids = gs.map((g, i) => {
    const cy = F.cy(i), by = px(cy - bh / 2), sum = ['min', 'q1', 'median', 'q3', 'max'].filter(k => isNum(g[k])).map(k => `${k} ${fmt(g[k], f)}`)
    return row(null, g.label, `${g.label}: ${sum.join(', ')}`, [g.band ? R(X(g.band[0]), px(cy - F.slot * 0.42), X(g.band[1]) - X(g.band[0]), px(F.slot * 0.84), 'dd-ok-band dd-band') : null,
      F.cells(i), o.range ? R(X(g.min), by, X(g.max) - X(g.min), bh, 'dd-range dd-mark dd-crisp')
        : [R(X(g.min), px(cy), X(g.max) - X(g.min), 1, 'dd-whisker dd-mark dd-crisp'), R(X(g.q1) + 0.5, by + 0.5, X(g.q3) - X(g.q1) - 1, bh - 1, 'dd-box dd-mark')],
      isNum(g.median) ? R(X(g.median) - 1, by - 2, 2, bh + 4, 'dd-median dd-mark dd-crisp') : null])
  })
  if (o.axis !== false) kids.push(axisX(sc, t, F.H + 2, f, e))
  return svg(e.W, F.H + (o.axis !== false ? axisH(e) + 2 : 0), join(o.title, gs.map(g => `${g.label} median ${fmt(g.median, f)}, ${fmt(g.min, f)} to ${fmt(g.max, f)}`).join('; ')), kids, 'dd-box-svg')
}

function scatter (input, o) {
  const e = env(o), { fs, sm, W, tw } = e, fx = o.formatX || 'int', fy = o.formatY || 'int'
  const sets = (Array.isArray(input) ? [{ name: o.name || '', points: input }] : input.sets).slice(0, 2)
  const H = px((o.height || 8) * e.u), pts = sets.flatMap(s => s.points), xs = pts.map(p => p.x), ys = pts.map(p => p.y)
  const top = px(sm * (o.yLabel ? 1.8 : 0.8)), bottom = H - px(sm * (o.xLabel ? 3.3 : 1.9))
  const ty = scaleFor(min(...ys), max(...ys), bottom - top, fy, e, false, true), x0 = yWidth(ty, fy, e)
  const x1 = W - Math.ceil(most(sets.map(s => tw(s.name || '', sm)))) - 8, tx = scaleFor(min(...xs), max(...xs), x1 - x0, fx, e)
  const sx = lin(tx.lo, tx.hi, x0, x1), sy = lin(ty.lo, ty.hi, bottom, top), r = max(3, fs * 0.3)
  const kids = [axisY(sy, ty, x0, top, bottom, fy, e), axisX(sx, tx, bottom, fx, e),
    o.yLabel ? T(x0, px(sm * 0.95), o.yLabel, sm, 'dd-t2') : null, o.xLabel ? T(x1, H - 3, o.xLabel, sm, 'dd-t2', END) : null]
  const taken = [], free = (x, y, w) => {
    const box = [x, y - sm * 0.75, x + w, y + sm * 0.2]
    if (box[0] < 0 || box[2] > W || taken.some(b => box[0] < b[2] && b[0] < box[2] && box[1] < b[3] && b[1] < box[3])) return false
    taken.push(box)
    return true
  }
  const fits = sets.map(s => {
    const n = s.points.length, mx = s.points.reduce((a, p) => a + p.x, 0) / n, my = s.points.reduce((a, p) => a + p.y, 0) / n
    const sxx = s.points.reduce((a, p) => a + (p.x - mx) ** 2, 0)
    if (o.fit === false || n < 2 || !sxx) return null
    const slope = s.points.reduce((a, p) => a + (p.x - mx) * (p.y - my), 0) / sxx, at = x => my + slope * (x - mx)
    const a = min(...s.points.map(p => p.x)), b = max(...s.points.map(p => p.x)), ly = clamp(sy(at(b)), top + sm, bottom) + mid(sm)
    if (s.name) free(sx(b) + 6, ly, tw(s.name, sm))
    return { a, b, at, ly }
  })
  sets.forEach((s, k) => {
    const f = fits[k]
    kids.push(s.points.map(p => h('circle', { cx: sx(p.x), cy: sy(p.y), r, class: `dd-ring dd-ring-${k} dd-mark` }, h('title', {}, `${p.label ? p.label + ': ' : ''}${fmt(p.x, fx)}, ${fmt(p.y, fy)}`))))
    if (f) kids.push(h('path', { d: `M${sx(f.a).toFixed(1)},${sy(f.at(f.a)).toFixed(1)}L${sx(f.b).toFixed(1)},${sy(f.at(f.b)).toFixed(1)}`, class: `dd-line dd-line-${k} dd-mark` }),
      s.name ? T(sx(f.b) + 6, f.ly, s.name, sm, 'dd-t2') : null)
    if (o.labels) {
      s.points.forEach(p => taken.push([sx(p.x) - r, sy(p.y) - r, sx(p.x) + r, sy(p.y) + r]))
      kids.push(s.points.filter(p => p.label).map(p => {
        const w = tw(p.label, sm), x = sx(p.x), y = sy(p.y), away = f && y > sy(f.at(p.x)) ? 1 : -1
        const spot = [[x + 1, away > 0 ? y + r + sm : y - r - 3], [x + r + 3, y + mid(sm)], [x - r - 3 - w, y + mid(sm)], [x + 1, away > 0 ? y - r - 3 : y + r + sm]].find(([a, b]) => free(a, b, w))
        return spot ? T(spot[0], spot[1], p.label, sm, 'dd-t2') : null
      }))
    }
  })
  return svg(W, H, join(o.title, sets.map(s => `${s.name || 'points'}, ${s.points.length} points`).join('; ')), kids, 'dd-scatter')
}

function squarify (sizes, x, y, w, h) {
  const k = w * h / (sizes.reduce((a, b) => a + b, 0) || 1), out = []
  const worst = (sum, hi, lo, side) => max(side * side * hi / (sum * sum), sum * sum / (side * side * lo))
  for (let i = 0; i < sizes.length;) {
    const side = min(w, h)
    let j = i + 1, sum = sizes[i] * k, hi = sum, lo = sum
    for (; j < sizes.length; j++) {
      const a = sizes[j] * k
      if (worst(sum + a, max(hi, a), min(lo, a), side) > worst(sum, hi, lo, side)) break
      sum += a; hi = max(hi, a); lo = min(lo, a)
    }
    const thick = sum / side
    let at = w >= h ? y : x
    for (let n = i; n < j; n++) {
      const len = sizes[n] * k / thick
      out.push(w >= h ? { x, y: at, w: thick, h: len } : { x: at, y, w: len, h: thick })
      at += len
    }
    if (w >= h) { x += thick; w -= thick } else { y += thick; h -= thick }
    i = j
  }
  return out
}
const HEAT = { ok: 1, warn: 3 }
function heat (m, st, policy) {
  if (st.level === 'alert') return 'a'
  if (!HEAT[st.level]) return 0
  const t = m.better === 'in' || !isNum(st.ratio) ? NaN : (1 - goodness(st.ratio, m.better)) / (1 - pol(m, policy).alert)
  return t > 0 && t < 1 ? 1 + min(3, Math.floor(t * 4)) : HEAT[st.level]
}
function treemap (input, o) {
  const e = env(o), { fs, sm, W, tw } = e, H = px((o.height || 10) * e.u)
  const grouped = input.some(g => Array.isArray(g.children))
  if (grouped && !input.every(g => Array.isArray(g.children))) throw new Error('dd.treemap: give every top-level entry children, or none')
  const cell = r => {
    if (r.children) throw new Error('dd.treemap: one level of grouping; fold the deeper levels into their groups')
    const m = norm(r, r.key), st = state(m, e.policy)
    return { m, st, size: isNum(r.size) ? r.size : m.value, heat: heat(m, st, e.policy) }
  }
  const groups = (grouped ? input : [{ children: input }]).map(g => {
    const cells = g.children.map(cell).filter(c => c.size > 0).sort((a, b) => b.size - a.size)
    return { label: g.label, cells, total: cells.reduce((s, c) => s + c.size, 0) }
  }).filter(g => g.total > 0).sort((a, b) => b.total - a.total)
  const gap = 1, gg = grouped ? max(2, px(fs * 0.4)) : 0, strip = grouped ? px(sm * 1.5) : 0, pad = max(2, px(sm * 0.3)), pitch = px(sm * 1.25)
  const sum = groups.reduce((s, g) => s + g.total, 0), WH = (W + gg) * (H + gg)
  const head = b => b.h - gg >= 2 * strip ? strip : 0, inner = b => max(0, b.w - gg) * max(0, b.h - gg - head(b))
  // A group's box also holds its header strip and gaps, which cost the most in a small group. Size each box as if square,
  // area − edge·√area + corner = k·total, then correct from the boxes' real shapes and keep the closest pass, since squarify jumps between arrangements.
  const edge = strip + 2 * gg, corner = gg * (strip + gg), need = k => groups.map(g => ((edge + Math.sqrt(max(0, edge * edge - 4 * corner + 4 * k * g.total))) / 2) ** 2)
  let lo = 0, hi = WH / sum
  for (let n = 0; n < 40; n++) { const k = (lo + hi) / 2; if (need(k).reduce((a, b) => a + b, 0) > WH) hi = k; else lo = k }
  let weights = need(lo), best = null
  for (let n = 0; n < 4; n++) {
    const boxes = squarify(weights, 0, 0, W + gg, H + gg), ins = boxes.map(inner), k = ins.reduce((a, b) => a + b, 0) / sum
    const err = max(...groups.map((g, i) => Math.abs(ins[i] / (k * g.total) - 1)))
    if (!best || err < best.err) best = { boxes, err }
    weights = groups.map((g, i) => g.total + (boxes[i].w * boxes[i].h - ins[i]) / k)
  }
  const kids = groups.map((g, i) => {
    const b = best.boxes[i], top = head(b), x0 = px(b.x), y0 = px(b.y), x1 = px(b.x + b.w) - gg, y1 = px(b.y + b.h) - gg
    const name = top && x1 > x0 ? clip(g.label ?? '', x1 - x0, sm, 600, tw) : ''
    const rs = x1 > x0 && y1 > y0 + top ? squarify(g.cells.map(c => c.size), x0, y0 + top, x1 - x0 + gap, y1 - y0 - top + gap) : []
    return h('g', { class: 'dd-tm-group' }, name && name !== '…' ? T(x0, y0 + top - px(sm * 0.45), name, sm, 'dd-t2', { 'font-weight': 600 }) : null, rs.map((r, j) => {
      const c = g.cells[j], m = c.m, st = c.st, cx = px(r.x), cy = px(r.y), w = px(r.x + r.w) - cx - gap, ht = px(r.y + r.h) - cy - gap
      const val = fmt(m.value, m.format), cls = c.heat === 'a' ? 'dd-knock' : 'dd-t', base = cy + pad + px(sm * 0.95)
      const one = tw(m.label, sm) + 2 * pad <= w && 2 * pad + pitch <= ht, two = one && tw(val, sm, DOTC[st.level] ? 700 : 400) + 2 * pad <= w && 2 * pad + 2 * pitch <= ht
      const title = [st.text, isNum(m.target) && `target ${fmt(m.target, m.format)}`, c.size !== m.value && `${o.sizeLabel || 'size'} ${fmt(c.size, o.sizeFormat || m.format)}`]
      return row(st.level, m.label, title.filter(Boolean).join('; '), [R(cx, cy, w, ht, `dd-heat-${c.heat} dd-crisp${c.heat === 'a' ? ' dd-mark' : ''}`),
        one ? T(cx + pad, base, m.label, sm, cls) : null, two ? T(cx + pad, base + pitch, val, sm, cls, bold(st.level)) : null], m.key)
    }))
  })
  return svg(W, H, join(o.title, groups.map(g => (g.label ? `${g.label}: ` : '') + g.cells.map(c => c.st.text).join('; ')).join('. ')), kids, 'dd-treemap')
}

function text (rows, o) {
  const cols = (o.cols || Object.keys(rows[0] || {})).map(c => typeof c === 'string' ? (([key, format, label]) => ({ key, format, label }))(c.split(':')) : c)
  const sts = rows.map(r => r.state || basis(r) ? state(norm(r), o.policy) : null), dots = sts.some(Boolean)
  const numeric = c => c.format || rows.some(r => isNum(r[c.key]))
  const cls = (...xs) => xs.filter(Boolean).join(' ') || null, fill = o.stretch == null ? cols.find(c => !numeric(c)) : cols.find(c => c.key === o.stretch)
  if (o.stretch != null && !fill) throw new Error(`dd.text: stretch "${o.stretch}" names no column; use one of ${cols.map(c => c.key).join(', ')}`)
  const lines = s => String(s).split('\n').map(l => h('span', { style: 'display:block' }, l))
  return String(h('table', { class: 'dd-text', 'aria-label': o.title || null },
    h('thead', {}, h('tr', {}, o.rank ? h('th', { class: 'dd-num dd-rank' }) : null, dots ? h('th', { class: 'dd-dotcell', style: `width:${dotCol(env(o).fs)}px` }) : null,
      cols.map(c => h('th', { class: cls(numeric(c) && 'dd-num') }, lines(c.label ?? c.key))))),
    h('tbody', {}, rows.map((r, i) => {
      const lv = sts[i] && sts[i].level
      return h('tr', { 'data-dd-level': lv, 'data-dd-label': lv ? r[cols[0].key] : null, 'data-dd-key': r.key, title: sts[i] && sts[i].text },
        o.rank ? h('td', { class: 'dd-num dd-rank' }, i + 1) : null,
        dots ? h('td', { class: 'dd-dotcell' }, new Raw(DOTC[lv] ? alert(lv, o) : '')) : null,
        cols.map(c => h('td', { class: cls(numeric(c) && 'dd-num', c === fill && 'dd-fill-col', c === fill && c.wrap && 'dd-wrap', DOTC[lv] && 'dd-strong'), title: c === fill ? r[c.key] : null },
          c.format ? fmt(r[c.key], c.format) : isNum(r[c.key]) ? fmt(r[c.key]) : r[c.key] ?? '')))
    }))))
}

const ICONS = {
  up: 'M.5,.12L.92,.85L.08,.85Z', down: 'M.5,.88L.92,.15L.08,.15Z',
  check: 'M.2,.5L.42,.8L.8,.2', x: 'M.2,.2L.8,.8M.8,.2L.2,.8', asterisk: 'M.5,.18L.5,.82M.22,.34L.78,.66M.22,.66L.78,.34'
}
function icon (kind, o, label, cls) {
  const fs = env(o).fs, s = px(fs), d = fs * DOT
  if (cls && !ICONS[kind]) throw new Error(`dd: icon "${kind}" is unknown; use ${Object.keys(ICONS).join(', ')}`)
  if (cls) return svg(s, s, label, h('path', { d: ICONS[kind].replace(/[\d.]+/g, v => +(v * s).toFixed(2)), class: cls }), 'dd-inline')
  return svg(d, d, label, alertDot(d / 2, d / 2, fs, kind), 'dd-inline', `vertical-align: ${+(mid(1) - DOT / 2).toFixed(2)}em`)
}
const alert = (level, o = {}) => icon(level, o, WORD[level] || level)
const trend = (dir, o = {}) => icon(dir, o, `trend ${dir}`, (o.bad ? 'dd-dot-alert' : 'dd-icon') + ' dd-mark')
const mark = (kind, o = {}) => icon(kind, o, kind, 'dd-icon-line')
function legend (items, o) {
  const e = env(o), { fs, tw, gap } = e, ht = px(fs * LINE), cy = ht / 2, s = px(fs * 0.75), kids = []
  let x = 0
  for (const it of items) {
    const k = it.mark, bar = k === 'bar' || k === 'projection', w = k === 'dot' ? px(fs * DOT) : bar || k === 'line' ? px(s * 1.6) : k === 'target' ? 4 : s
    const th = bar ? max(3, px(s / 3)) : k === 'line' ? 2 : k === 'target' ? s + 2 : s
    const cls = { bar: 'dd-bar', projection: 'dd-proj', target: 'dd-tgt', band: `dd-band dd-band-${it.tone ?? 2}`, fill: 'dd-fill', highlight: 'dd-fill-hi', part: `dd-part-${it.tone ?? 0}`, line: `dd-part-${it.tone ?? 0}`, heat: `dd-heat-${it.tone ?? 0}` }[k]
    kids.push(k === 'dot' ? alertDot(x + w / 2, cy, fs, it.level || 'alert') : cls ? R(x + (k === 'target' ? 1 : 0), px(cy - th / 2), k === 'target' ? 2 : w, th, cls) : null,
      T(x + w + 4, cy + mid(fs), it.label, fs, 'dd-t2'))
    x += w + 4 + tw(it.label, fs) + gap
  }
  return svg(Math.ceil(x - gap), ht, items.map(i => i.label).join(', '), kids, 'dd-inline')
}

const RANK = { warn: 1, alert: 2 }
function flagged (root = document) {
  const rows = new Map()
  for (const el of root.querySelectorAll('[data-dd-level]')) {
    const level = el.getAttribute('data-dd-level'), id = el.getAttribute('data-dd-key') || el, was = rows.get(id)
    if (!was || (RANK[level] || 0) > (RANK[was.level] || 0)) rows.set(id, { level, label: el.getAttribute('data-dd-label') || '' })
  }
  const out = { total: rows.size, alert: [], warn: [] }
  for (const r of rows.values()) if (RANK[r.level]) out[r.level].push(r.label)
  return out
}
function flags (rows, o) {
  const parts = ['alert', 'warn'].map(lv => [lv, (rows[lv] || []).length]).filter(([, n]) => n)
  if (!parts.length) return String(h('span', {}, 'Nothing flagged'))
  const fs = env(o).fs, d = Math.ceil(fs * 0.7), pip = lv => new Raw(svg(d, d, null, dot(d / 2, d / 2, fs * 0.35, lv), 'dd-inline', 'vertical-align: 0'))
  const said = (lv, n) => `${n} ${lv === 'alert' ? 'critical' : n === 1 ? 'warning' : 'warnings'}`
  return String(h('span', { title: parts.map(([lv]) => `${WORD[lv][0].toUpperCase()}${WORD[lv].slice(1)}: ${rows[lv].join(', ')}`).join('. ') },
    parts.map(([lv, n], i) => [i ? ' · ' : null, pip(lv), ' ', said(lv, n)])))
}

const ro = typeof ResizeObserver === 'function' && new ResizeObserver(es => es.forEach(en => en.target.ddRender && en.target.ddRender()))
const counters = new Set()
let recounting = false
const recount = () => {
  if (recounting || !counters.size) return
  recounting = true
  queueMicrotask(() => { recounting = false; counters.forEach(el => el.ddRender(true)) })
}
const mount = (name, draw) => (target, input, o = {}) => {
  const el = typeof target === 'string' ? document.querySelector(target) : target
  if (!el) throw new Error(`dd.${name}: nothing on the page matches ${target}`)
  let last = ''
  el.ddRender = force => {
    const cs = getComputedStyle(el), u = parseFloat(cs.fontSize) / 0.625, width = el.clientWidth, key = width + ' ' + u
    if (key === last && !force) return
    last = key
    el.innerHTML = draw(input, { ...o, width, u, measure: measurer(cs.fontFamily) })
    if (!counters.has(el)) recount()
  }
  el.classList.add('dd-mount')
  el.ddRender()
  if (ro) ro.observe(el)
  return el
}
function layout () {
  const doc = document.documentElement
  const cols = parseFloat(getComputedStyle(doc).getPropertyValue('--dd-cols')) || 72
  doc.dataset.ddLayout = innerWidth / cols * 0.625 < 11 ? 'column' : 'grid'
}

const media = { table, bullet, spark, bars, stacked, line, box, scatter, treemap, text, legend, alert, trend, mark }
function fmtIn (v, s, locale) {
  const was = now.locale
  now.locale = locale || was
  try { return fmt(v, s) } finally { now.locale = was }
}
const api = { version: VERSION, fmt: fmtIn, asOf, state, data, flagged, svg: {} }
for (const [k, f] of Object.entries(media)) {
  api.svg[k] = (input, o) => f(input, o || {})
  api[k] = mount(k, f)
}
api.svg.flags = (rows, o) => flags(rows, o || {})
api.flags = (target, o) => {
  const el = mount('flags', (_, opts) => flags(flagged(), opts))(target, null, o)
  counters.add(el)
  return el
}
const INSTEAD = { pie: 'dd.bars with pctTotal', donut: 'dd.bars with pctTotal', gauge: 'dd.bullet', radar: 'dd.bars', area: 'dd.line, or dd.stacked for parts of a whole' }
for (const [k, use] of Object.entries(INSTEAD)) {
  api[k] = api.svg[k] = () => { throw new Error(`dd.${k}: a Few dashboard draws no ${k} charts (mistake 5); use ${use}`) }
}
globalThis.DataDashboard = Object.freeze(api)

if (typeof document !== 'undefined') {
  layout()
  addEventListener('resize', () => {
    layout()
    document.querySelectorAll('.dd-mount').forEach(el => el.ddRender && el.ddRender())
  })
}
})()
