// Behavior tests for assets/dashboard.js through its pure dd.svg.* functions, measured with the
// library's own estimate. Run: node lib_test.mjs
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import vm from 'node:vm'

const LIB = fileURLToPath(new URL('../skills/data-dashboard/assets/dashboard.js', import.meta.url))
vm.runInThisContext(readFileSync(LIB, 'utf8'))
const dd = globalThis.DataDashboard

const attrs = s => Object.fromEntries([...s.matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]]))
const rects = (svg, cls) => [...svg.matchAll(/<rect ([^>]*)>/g)].map(m => attrs(m[1]))
  .filter(a => a.class.split(' ').includes(cls)).map(a => ({ x: +a.x, y: +a.y, w: +a.width, h: +a.height, cls: a.class }))
const texts = svg => [...svg.matchAll(/<text ([^>]*)>([^<]*)<\/text>/g)].map(m => ({ ...attrs(m[1]), s: m[2] }))
const text = (svg, s) => texts(svg).find(t => t.s === s)
const rows = svg => svg.split('<g ').slice(1)
const level = g => /data-dd-level="(\w+)"/.exec(g)[1]

// The band holding the bar's end, counted from the bad end: 0 is the darkest.
function bandAtBar (g) {
  const bar = rects(g, 'dd-bar')[0], end = bar.x + bar.w
  const bands = rects(g, 'dd-band').sort((a, b) => a.x - b.x)
  return { i: bands.findIndex(b => end > b.x && end <= b.x + b.w), n: bands.length }
}
const expected = { alert: 0, warn: 1 }

let seed = 7
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647
const cellsOf = svg => [...svg.matchAll(/<g data-dd-level="(\w+)"[^>]*>(?:<title>([^<]*)<\/title>)?<rect ([^>]*)><\/rect>(.*?)<\/g>/g)].map(m => {
  const a = attrs(m[3])
  return { level: m[1], title: m[2], x: +a.x, y: +a.y, w: +a.width, h: +a.height, cls: a.class, texts: texts(m[4]) }
})
const groupsOf = svg => svg.split('<g class="dd-tm-group">').slice(1).map(s => ({ head: texts(s.split('<g data-dd-level')[0])[0], cells: cellsOf(s) }))
const overlap = (a, b) => Math.min(a.x + a.w, b.x + b.w) > Math.max(a.x, b.x) && Math.min(a.y + a.h, b.y + b.h) > Math.max(a.y, b.y)
const bbox = cs => { const x = Math.min(...cs.map(c => c.x)), y = Math.min(...cs.map(c => c.y)); return { x, y, w: Math.max(...cs.map(c => c.x + c.w)) - x, h: Math.max(...cs.map(c => c.y + c.h)) - y } }
const randomMap = () => {
  const items = n => Array.from({ length: n }, (_, i) => ({ label: `c${i}`, value: Math.round(10 + rnd() ** 2 * 1000), target: 500 }))
  const input = rnd() < 0.7 ? Array.from({ length: 1 + Math.floor(rnd() * 6) }, (_, g) => ({ label: `G${g}`, children: items(1 + Math.floor(rnd() * 10)) })) : items(3 + Math.floor(rnd() * 30))
  return { input, o: { width: 300 + Math.floor(rnd() * 500), u: 20, height: 6 + Math.floor(rnd() * 10) } }
}

const tests = {
  'a measure\'s own policy sets its bands as well as its dot (table and bullet)' () {
    const m = { label: 'On-time delivery', value: 0.962, target: 1, format: 'pct1', policy: { warn: 0.98, alert: 0.95 } }
    const page = { warn: 0.95, alert: 0.85 }
    for (const svg of [dd.svg.table([m], { width: 500, policy: page }), dd.svg.table([m], { width: 500, policy: page, scale: 'own' }), dd.svg.bullet(m, { width: 500, policy: page })]) {
      const g = rows(svg)[0]
      assert.equal(level(g), 'warn')
      assert.equal(bandAtBar(g).i, expected.warn, 'bar ends in the warning band')
    }
  },
  'scale shared: one axis in the measures\' units, one continuous target line' () {
    const r = (label, value) => ({ label, value, target: 5, ranges: [2, 3, 5], format: 'dec1' })
    const svg = dd.svg.table([r('O−', 1.6), r('A+', 4.4), r('AB+', 8.1)], { scale: 'shared', width: 600, cols: ['label', 'graph', 'value'] })
    const axes = rects(svg, 'dd-axis').filter(a => a.h === 1 && a.w > 100)
    assert.equal(axes.length, 1, 'one axis at the foot')
    assert.ok(texts(svg).some(t => t.s === '8') && !texts(svg).some(t => t.s.includes('%')), 'ticks in days')
    const tg = rects(svg, 'dd-tgt')
    assert.equal(tg.length, 1, 'one target line')
    assert.ok(tg[0].h > 2 * rects(svg, 'dd-band')[0].h, 'the line runs through every row')
    const bars = rects(svg, 'dd-bar').map(b => b.w)
    assert.ok(Math.abs(bars[2] / bars[0] - 8.1 / 1.6) < 0.1, 'bars in proportion to the values')
    const g = rows(svg)[0], edges = rects(g, 'dd-band').map(b => b.x).sort((a, b) => a - b)
    const sc = v => edges[0] + v / 8.1 * (rects(g, 'dd-band').reduce((s, b) => s + b.w, 0))
    assert.equal(edges.length, 4, 'bands from the row\'s own three breaks')
    assert.ok(edges[1] < sc(2.5), 'first break near 2 days')
  },
  'scale shared: a target tick per row when the targets differ' () {
    const svg = dd.svg.table([{ label: 'Reno', value: 6.2, target: 5 }, { label: 'Joliet', value: 7.4, target: 6 }], { scale: 'shared', width: 600 })
    const tg = rects(svg, 'dd-tgt')
    assert.equal(tg.length, 2)
    assert.ok(tg.every(t => t.h < 20), 'ticks, not one line')
    assert.throws(() => dd.svg.table([{ label: 'x', value: 1, target: 1 }], { scale: 'units' }), /scale/)
  },
  'the label column is as wide as its header' () {
    const svg = dd.svg.table([{ label: 'O−', value: 27, target: 30 }, { label: 'AB+', value: 11, target: 10 }],
      { width: 400, cols: ['alert', 'label', 'graph', 'value'], head: { label: 'Booked by type', graph: '% of goal', value: 'Booked' } })
    const a = text(svg, 'Booked by type'), b = text(svg, '% of goal')
    assert.ok(+b.x - +a.x >= 'Booked by type'.length * +a['font-size'] * 0.55, `graph header at ${b.x} collides with label header at ${a.x}`)
  },
  'the graph header stops a gap short of the value header' () {
    const head = { label: 'Type', graph: '% of booking goal', value: 'Booked' }
    const svg = dd.svg.table([{ label: 'O−', value: 27, target: 40 }], { width: 200, cols: ['alert', 'label', 'graph', 'value'], head })
    const g = texts(svg).find(t => t.s.startsWith('% of')), v = text(svg, 'Booked'), w = s => s.length * +g['font-size'] * 0.55
    assert.ok(+g.x + w(g.s) <= +v.x - w(v.s) - 6, `"${g.s}" ends at ${(+g.x + w(g.s)).toFixed(0)}, "Booked" starts at ${(+v.x - w(v.s)).toFixed(0)}`)
    const wide = texts(dd.svg.table([{ label: 'O−', value: 27, target: 40 }], { width: 600, cols: ['alert', 'label', 'graph', 'value'], head }))
    assert.ok(wide.some(t => t.s === head.graph), 'a header that fits is left whole')
  },
  'dd.text: stretch names the column that takes the extra width; the rest stay on one line' () {
    const data = [{ expires: 'Mon, Nov 16', where: 'Blood center', units: 7 }]
    const html = dd.svg.text(data, { cols: [{ key: 'expires', label: 'Expires', wrap: true }, 'where::Held at', 'units:int:Units'], stretch: 'where' })
    const tds = [...html.matchAll(/<td([^>]*)>/g)].map(m => m[1])
    assert.match(tds[1], /dd-fill-col/)
    assert.doesNotMatch(tds[0], /dd-fill-col|dd-wrap/)
    assert.throws(() => dd.svg.text(data, { cols: ['where::Held at'], stretch: 'nope' }), /stretch/)
    const plain = [...dd.svg.text(data, { cols: ['expires::Expires', 'where::Held at'] }).matchAll(/<td([^>]*)>/g)].map(m => m[1])
    assert.match(plain[0], /dd-fill-col/, 'the first text column stretches by default')
  },
  'labelWidth and valueWidth line two tables up' () {
    const o = { width: 500, labelWidth: 6, valueWidth: '60px' }
    const a = dd.svg.table([{ label: 'Revenue', units: 'U.S. $', value: 5900000, target: 7500000, format: 'usd0k', history: [1, 2] }], o)
    const b = dd.svg.table([{ label: 'ERP', value: 0.98, target: 0.99, format: 'pct1', history: [1, 2] }], { ...o, scale: 'own' })
    const x0 = s => Math.min(...rects(s, 'dd-band').map(r => r.x)), x1 = s => Math.max(...rects(s, 'dd-band').map(r => r.x + r.w))
    assert.equal(x0(a), x0(b), 'graphs start together')
    assert.equal(x1(a), x1(b), 'graphs end together')
    assert.equal(500 - x1(a), 60 + Math.round(12.5 * 0.8), 'value column is 60 px plus the gap')
  },
  'dd.legend draws a projection mark' () {
    const svg = dd.svg.legend([{ mark: 'bar', label: 'Booked' }, { mark: 'projection', label: 'With walk-ins' }], {})
    assert.equal(rects(svg, 'dd-proj').length, 1)
  },
  'a sparkline is scaled to its data, and its normal band clipped to the plot' () {
    const m = { label: 'O−', value: 1.6, target: 5, norm: [3, 7], history: [4.6, 4.3, 3.8, 3.3, 2.6, 2.1, 1.6] }
    const svg = dd.svg.spark(m, { width: 200, text: false })
    const ys = [.../d="M([^"]+)"/.exec(svg)[1].matchAll(/,([\d.]+)/g)].map(x => +x[1]), H = +/height="([\d.]+)"/.exec(svg)[1]
    assert.ok(Math.max(...ys) - Math.min(...ys) >= H - 6, `a 3-day fall spans ${(Math.max(...ys) - Math.min(...ys)).toFixed(1)} of ${H} px`)
    const band = rects(svg, 'dd-norm')[0]
    assert.equal(band.y, 0, 'band runs to the top of the plot')
    assert.ok(band.y + band.h < H, 'band stops at 3 days, above the lowest point')
  },
  'a sparkline draws its normal band only when the line leaves it' () {
    const inside = { label: 'A+', value: 4.4, target: 5, norm: [3, 7], history: [5, 4.8, 4.6, 4.7, 4.4] }
    const leaves = { ...inside, history: [5, 4.8, 4.1, 3.3, 2.7] }
    for (const o of [{ width: 200, text: false }, { width: 500, cols: ['spark', 'label', 'value'] }]) {
      const draw = m => o.cols ? dd.svg.table([m], o) : dd.svg.spark(m, o)
      assert.equal(rects(draw(inside), 'dd-norm').length, 0, 'every point inside the band: no gray box')
      assert.equal(rects(draw(leaves), 'dd-norm').length, 1, 'a point below the band: the band shows where normal ends')
    }
  },
  'alert dots are a line of text tall in every medium, clear of the label beside them' () {
    const u = 20, fs = 12.5, page = 72 * u
    const dots = s => [...s.matchAll(/<circle ([^>]*)>/g)].map(m => attrs(m[1])).filter(a => /dd-dot-(alert|warn)/.test(a.class)).map(a => ({ x: +a.cx, y: +a.cy, r: +a.r }))
    const m = (label, value) => ({ label, value, target: 100, units: 'units', history: [100, 90, value] })
    const cases = {
      table: dd.svg.table([m('Profit', 70), m('Revenue', 90)], { width: 600, u }),
      bullet: dd.svg.bullet([m('Profit', 70)], { width: 600, u }),
      bars: dd.svg.bars([{ label: 'Middle East', value: 39, target: 50 }, { label: 'Europe', value: 90, target: 80 }], { width: 600, u }),
      stacked: dd.svg.stacked([{ label: 'Asia', actual: 30, pipeline: 10, target: 50 }], { width: 600, u, alertWhen: 'sumBelowTarget' })
    }
    for (const [name, svg] of Object.entries(cases)) {
      const ds = dots(svg).filter(d => d.r > 3)
      assert.ok(ds.length, `${name} draws an alert dot`)
      for (const d of ds) {
        assert.ok(2 * d.r >= 1.3 * fs - 0.01, `${name}: dot ${2 * d.r} px across, under a 16 px line`)
        assert.ok(2 * d.r / page >= 0.011, `${name}: dot is ${(200 * d.r / page).toFixed(2)}% of the page width`)
        const label = texts(svg).filter(t => Math.abs(+t.y - d.y) < fs && t['text-anchor'] !== 'end' && +t.x > d.x).sort((a, b) => a.x - b.x)[0]
        if (label) assert.ok(+label.x - (d.x + d.r) >= 0.4 * fs - 0.5, `${name}: ${(+label.x - d.x - d.r).toFixed(1)} px between the dot and "${label.s}"`)
      }
    }
    assert.equal(dots(cases.table).filter(d => d.r <= 3).length, 2, 'the sparkline end dots stay small')
    const legend = dd.svg.legend([{ mark: 'dot', level: 'alert', label: 'Critical' }], { u: 17.6 })
    assert.ok(2 * dots(legend)[0].r >= 1.3 * 11 - 0.01, 'a legend dot keys the dots at its own type size')
    const icon = dd.svg.alert('warn', { u })
    assert.ok(2 * dots(icon)[0].r >= 1.3 * fs - 0.01 && +attrs(icon).height >= 2 * dots(icon)[0].r - 0.02,'dd.alert is the same dot, inside its box')
    const html = dd.svg.text([{ name: 'Budgeting', days: -13, state: 'alert' }, { name: 'ERP', days: 4, state: 'good' }], { u })
    assert.ok(2 * dots(html)[0].r >= 1.3 * fs - 0.01, 'a text table row gets the same dot')
    assert.match(html, /<th class="dd-dotcell" style="width:\d+px">/, 'the dot column keeps its width when no row is flagged')
  },
  'treemap: areas follow size, exactly within a group and within 3% across the map for 95% of cells' () {
    seed = 7
    const errs = []
    for (let trial = 0; trial < 300; trial++) {
      const { input, o } = randomMap(), svg = dd.svg.treemap(input, o)
      const size = c => +/ ([\d,]+) /.exec(c.title)[1].replace(/,/g, ''), slot = c => (c.w + 1) * (c.h + 1)
      for (const g of groupsOf(svg)) {
        const k = g.cells.reduce((a, c) => a + slot(c), 0) / g.cells.reduce((a, c) => a + size(c), 0)
        for (const c of g.cells) assert.ok(Math.abs(slot(c) - k * size(c)) <= c.w + c.h + 2, `trial ${trial}: in its group a ${c.w}x${c.h} cell is off its share by more than rounding its edges`)
      }
      const cs = cellsOf(svg), k = cs.reduce((a, c) => a + slot(c), 0) / cs.reduce((a, c) => a + size(c), 0)
      assert.equal(cs.length, input.flatMap(g => g.children || [g]).length, `trial ${trial}: every item with a size is drawn`)
      for (const c of cs) if (Math.min(c.w, c.h) >= 20) errs.push(Math.abs(slot(c) / (k * size(c)) - 1))
    }
    errs.sort((a, b) => a - b)
    const at = p => errs[Math.floor(p * (errs.length - 1))]
    assert.ok(at(0.5) <= 0.01 && at(0.95) <= 0.03 && at(1) <= 0.35, `across ${errs.length} cells 20 px or more on a side: median ${(100 * at(0.5)).toFixed(1)}%, 95th percentile ${(100 * at(0.95)).toFixed(1)}%, worst ${(100 * at(1)).toFixed(1)}%`)
  },
  'treemap: every cell sits inside its group, under its header, and no two cells overlap' () {
    seed = 11
    for (let trial = 0; trial < 150; trial++) {
      const { input, o } = randomMap(), svg = dd.svg.treemap(input, o), H = +/<svg [^>]*height="(\d+)"/.exec(svg)[1]
      const gs = groupsOf(svg), cs = gs.flatMap(g => g.cells)
      for (const c of cs) assert.ok(c.x >= 0 && c.y >= 0 && c.x + c.w <= o.width && c.y + c.h <= H, `trial ${trial}: a cell leaves the treemap`)
      cs.forEach((a, i) => cs.slice(i + 1).forEach(b => assert.ok(!overlap(a, b), `trial ${trial}: cells overlap`)))
      const boxes = gs.map(g => bbox(g.cells))
      boxes.forEach((a, i) => boxes.slice(i + 1).forEach(b => assert.ok(!overlap(a, b), `trial ${trial}: two groups' cells mix`)))
      gs.forEach((g, i) => { if (g.head) assert.ok(+g.head.y <= boxes[i].y && +g.head.x === boxes[i].x, `trial ${trial}: a header sits off its group`) })
    }
    const flat = dd.svg.treemap([{ label: 'a', value: 2, target: 1 }, { label: 'b', value: 1, target: 1 }], { width: 300 })
    assert.equal(groupsOf(flat).length, 1)
    assert.equal(groupsOf(flat)[0].head, undefined, 'flat items have no header strip')
    assert.throws(() => dd.svg.treemap([{ label: 'g', children: [] }, { label: 'x', value: 1 }], {}), /children/)
    assert.throws(() => dd.svg.treemap([{ label: 'g', children: [{ label: 'h', children: [] }] }], {}), /one level/)
  },
  'treemap: squarified cells are near square' () {
    const aspect = c => Math.max((c.w + 1) / (c.h + 1), (c.h + 1) / (c.w + 1)), mean = xs => xs.reduce((a, b) => a + b) / xs.length
    const sizes = [100, 80, 60, 50, 40, 30, 25, 20, 15, 12, 10, 8, 6, 5], total = sizes.reduce((a, b) => a + b)
    const as = cellsOf(dd.svg.treemap(sizes.map((v, i) => ({ label: `c${i}`, value: v, target: v })), { width: 600, height: 10 })).map(aspect)
    const slices = mean(sizes.map(s => Math.max(200 / (600 * s / total), 600 * s / total / 200)))
    assert.ok(mean(as) <= 1.7, `mean aspect ${mean(as).toFixed(2)}, against ${slices.toFixed(1)} for one row of slices`)
    assert.ok(Math.max(...as) <= 4, `worst aspect ${Math.max(...as).toFixed(2)}`)
    seed = 17
    const flat = []
    for (let trial = 0; trial < 200; trial++) {
      const items = Array.from({ length: 5 + Math.floor(rnd() * 25) }, (_, i) => ({ label: `c${i}`, value: Math.round(10 + rnd() ** 2 * 1000), target: 500 }))
      flat.push(...cellsOf(dd.svg.treemap(items, { width: 400 + Math.floor(rnd() * 300), height: 8 + Math.floor(rnd() * 6) })).map(aspect))
    }
    assert.ok(mean(flat) <= 1.6, `mean aspect ${mean(flat).toFixed(2)} over ${flat.length} cells of 200 random maps`)
  },
  'treemap: color runs from neutral at target to the alert red under the alert threshold, as the state does' () {
    const ratios = [1.2, 1, 0.99, 0.97, 0.95, 0.93, 0.91, 0.89, 0.87, 0.86, 0.84, 0.5]
    const cs = cellsOf(dd.svg.treemap(ratios.map((r, i) => ({ label: `c${i}`, key: `c${i}`, value: r * 100, target: 100, size: 10 })), { width: 600, height: 10, policy: { warn: 0.95, alert: 0.85 } }))
      .sort((a, b) => parseFloat(b.title.split(' ')[1]) - parseFloat(a.title.split(' ')[1]))
    const step = c => c.cls.match(/dd-heat-(\w)/)[1]
    assert.deepEqual([step(cs[0]), step(cs[1])], ['0', '0'], 'at or above target: neutral')
    assert.deepEqual([step(cs[10]), step(cs[11])], ['a', 'a'], 'under the alert threshold: the alert red')
    const mid = cs.slice(2, 10).map(step)
    assert.ok(mid.every(s => /[1-4]/.test(s)) && mid.every((s, i) => i === 0 || s >= mid[i - 1]), `tints between, darkening as the ratio falls: ${mid}`)
    assert.ok(mid.includes('1') && mid.includes('4'), `the tints span the ramp: ${mid}`)
    for (const c of cs) {
      assert.equal(step(c) === 'a', c.level === 'alert', `${c.title}: alert red exactly when the state is critical`)
      assert.equal(step(c) === '0', c.level === 'good', `${c.title}: neutral exactly when the state is good`)
      assert.ok(c.title.includes(`, ${{ alert: 'critical', warn: 'warning', ok: 'satisfactory', good: 'good' }[c.level]}; target 100; size 10`), `${c.title} names its state, target and size`)
    }
    const down = cellsOf(dd.svg.treemap([{ label: 'Cost', value: 116, target: 100, better: 'down', size: 1 }, { label: 'Spend', value: 90, target: 100, better: 'down', size: 1 }], { width: 300 }))
    assert.deepEqual(down.map(step), ['a', '0'], 'lower is better mirrors the ramp')
    const forced = cellsOf(dd.svg.treemap([{ label: 'Forced', value: 120, target: 100, state: 'alert' }], { width: 300 }))
    assert.equal(step(forced[0]), 'a', 'an explicit state wins')
    assert.match(forced[0].cls, /dd-mark/, 'an alert cell is a mark, held to 3:1 against the page')
  },
  'treemap: a label and its value are drawn only when they fit, and never clipped' () {
    const items = [{ label: 'California', value: 5900000, target: 7200000, format: 'usd0k', size: 900 },
      { label: 'Rhode Island and Providence Plantations', value: 90000, target: 100000, format: 'usd0k', size: 6 },
      { label: 'Ohio', value: 1200000, target: 1100000, format: 'usd0k', size: 120 }]
    const cs = cellsOf(dd.svg.treemap(items, { width: 400, height: 8 }))
    const by = l => cs.find(c => c.title.startsWith(l))
    assert.deepEqual(by('California').texts.map(t => t.s), ['California', '$5,900K'], 'a big cell shows its label and value')
    assert.deepEqual(by('Rhode').texts, [], 'a label too long for its cell is left out, not cut')
    assert.match(by('Rhode').title, /Rhode Island and Providence Plantations 90 thousand dollars, 90% of target/, 'its exact values are in its title')
    seed = 13
    for (let trial = 0; trial < 150; trial++) {
      const { input, o } = randomMap()
      for (const c of cellsOf(dd.svg.treemap(input, o))) {
        for (const t of c.texts) {
          const size = +t['font-size'], w = t.s.length * size * (t['font-weight'] > 500 ? 0.6 : 0.55)
          assert.ok(!t.s.includes('…'), `"${t.s}" is ellipsized`)
          assert.ok(+t.x >= c.x && +t.x + w <= c.x + c.w && +t.y - size <= c.y + c.h && +t.y - size * 0.8 >= c.y && +t.y + size * 0.25 <= c.y + c.h, `trial ${trial}: "${t.s}" leaves its ${c.w}x${c.h} cell`)
        }
      }
    }
  },
  'treemap: dd.flagged counts its critical and warning cells, once each by key' () {
    const page = (...parts) => ({ querySelectorAll: () => parts.join('').match(/<(?:g|tr) [^>]*data-dd-level[^>]*>/g).map(t => ({ getAttribute: k => attrs(t)[k] ?? null })) })
    const svg = dd.svg.treemap([{ label: 'West', children: [{ label: 'California', key: 'ca', value: 80, target: 100 }, { label: 'Oregon', key: 'or', value: 92, target: 100 }] },
      { label: 'East', children: [{ label: 'New York', key: 'ny', value: 104, target: 100 }] }], { width: 400 })
    const again = dd.svg.table([{ label: 'California', key: 'ca', value: 80, target: 100 }], { width: 400 })
    assert.deepEqual(dd.flagged(page(svg, again)), { total: 3, alert: ['California'], warn: ['Oregon'] })
    assert.match(svg, /aria-label="West: Oregon 92, 92% of target, warning; California 80, 80% of target, critical\. East: New York 104, 104% of target, good"/, 'the name lists every cell by group, largest first')
  },
  'dd.flagged counts each flagged row once, by measure key, and dd.svg.flags says it' () {
    const page = (...parts) => ({ querySelectorAll: () => parts.join('').match(/<(?:g|tr) [^>]*data-dd-level[^>]*>/g).map(t => ({ getAttribute: k => attrs(t)[k] ?? null })) })
    const ms = { oNeg: { label: 'O−', value: 1.6, target: 5, ranges: [2, 3, 5], history: [3, 2, 1.6] },
      oNegBooked: { label: 'O−', value: 30, target: 40, ranges: [24, 32, 40] }, aPos: { label: 'A+', value: 4.4, target: 5, ranges: [2, 3, 5] } }
    const shown = page(
      dd.svg.table(ms, { rows: ['oNeg', 'aPos'], width: 600 }),
      dd.svg.table(ms, { rows: ['oNegBooked'], width: 600 }),
      dd.svg.bullet({ ...ms.oNeg, key: 'oNeg' }, { width: 600 }),
      dd.svg.bars([{ label: 'Middle East', value: 39, target: 50 }], { width: 600 }),
      dd.svg.legend([{ mark: 'dot', level: 'alert', label: 'Critical' }], {}))
    const rows = dd.flagged(shown)
    assert.deepEqual(rows.alert, ['O−', 'Middle East'], 'O− at the center counts once though drawn in a table and a bullet, with its sparkline end dot')
    assert.deepEqual(rows.warn, ['O−'], 'O− bookings is another measure with the same label, so it counts')
    assert.equal(rows.total, 4, 'the legend swatch is not a row')
    const line = s => s.replace(/<svg[^]*?<\/svg>/g, '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()
    const svg = dd.svg.flags(rows, {})
    assert.equal(line(svg), '2 critical · 1 warning')
    assert.equal((svg.match(/dd-dot-alert/g) || []).length, 1, 'one dot of each level')
    assert.equal((svg.match(/dd-dot-warn/g) || []).length, 1)
    assert.match(svg, /aria-hidden="true"/, 'the dots are decoration; the words carry the count')
    assert.equal(line(dd.svg.flags({ alert: [], warn: ['a', 'b', 'c', 'd'] }, {})), '4 warnings')
    assert.equal(line(dd.svg.flags({ alert: [], warn: [] }, {})), 'Nothing flagged')
    assert.doesNotMatch(dd.svg.flags({ alert: [], warn: [] }, {}), /<circle/)
  }
}

let failed = 0
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log(`ok   ${name}`) } catch (err) { failed++; console.log(`FAIL ${name}\n     ${err.message.split('\n')[0]}`) }
}
process.exit(failed ? 1 : 0)
