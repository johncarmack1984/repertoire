/* data-dashboard check: measures a page drawn with the library and writes #dd-report. dashboard.py check inlines it after the library in a temporary copy of the page, so no page carries it. MIT license. */
(() => {
'use strict'
const dd = globalThis.DataDashboard
const { round: px, max, min } = Math
const errors = []
addEventListener('error', ev => errors.push(String(ev.message || ev.error)))
addEventListener('unhandledrejection', ev => errors.push(String((ev.reason && ev.reason.message) || ev.reason)))

const rgba = c => {
  const m = /rgba?\(([^)]+)\)/.exec(c || '')
  if (!m) return null
  const p = m[1].split(/[\s,/]+/).filter(Boolean).map(parseFloat)
  return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]
}
const lum = c => c.slice(0, 3).reduce((s, v, i) => { v /= 255; return s + [0.2126, 0.7152, 0.0722][i] * (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4) }, 0)
const over = (c, bg) => c[3] >= 1 ? c : [0, 1, 2].map(i => c[i] * c[3] + bg[i] * (1 - c[3])).concat(1)
const contrast = (a, b) => { const x = lum(a) + 0.05, y = lum(b) + 0.05; return +(max(x, y) / min(x, y)).toFixed(2) }
const hex = c => '#' + c.slice(0, 3).map(v => px(v).toString(16).padStart(2, '0')).join('').toUpperCase()
const chroma = c => (max(...c.slice(0, 3)) - min(...c.slice(0, 3))) / 255

function check () {
  const doc = document.documentElement, body = document.body, cs = el => getComputedStyle(el)
  const bgOf = el => {
    for (; el && el.nodeType === 1; el = el.parentElement) { const c = rgba(cs(el).backgroundColor); if (c && c[3] > 0) return over(c, [255, 255, 255, 1]) }
    return [255, 255, 255, 1]
  }
  const secOf = el => el.closest('main section, .dd-sec, header, footer')
  const nameOf = s => !s ? 'page' : ((s.querySelector('h1, h2, h3') || {}).textContent || s.id || s.tagName.toLowerCase()).trim().replace(/\s+/g, ' ').slice(0, 48)
  const where = el => `${nameOf(secOf(el))} ${el.tagName.toLowerCase()}${el.getAttribute('class') ? '.' + el.getAttribute('class').split(/\s+/)[0] : ''}`
  const meet = (a, b) => [min(a.right, b.right) - max(a.left, b.left), min(a.bottom, b.bottom) - max(a.top, b.top)]
  const rep = {
    version: dd.version, viewport: { w: innerWidth, h: innerHeight }, layout: doc.dataset.ddLayout || 'grid',
    page: { w: doc.scrollWidth, h: doc.scrollHeight }, fontPx: parseFloat(cs(body).fontSize), sections: [], overlaps: [], clipped: [], collide: [],
    small: [], contrast: [], marks: [], colors: [], rows: { total: 0, warn: [], alert: [] }, groups: 0, noComparison: [], asOf: null, errors
  }
  const secs = [...document.querySelectorAll('main section, .dd-sec')], rects = secs.map(s => s.getBoundingClientRect())
  rep.groups = secs.length
  const foot = document.querySelector('body > footer, .dd-foot')
  rep.footTop = foot ? px(foot.getBoundingClientRect().top) : null
  secs.forEach((s, i) => {
    const r = rects[i]
    rep.sections.push({ name: nameOf(s), x: px(r.left), y: px(r.top), w: px(r.width), h: px(r.height), bottom: px(r.bottom), right: px(r.right) })
    for (let j = i + 1; j < secs.length; j++) {
      const [w, ht] = meet(r, rects[j])
      if (w > 1 && ht > 1) rep.overlaps.push({ a: nameOf(s), b: nameOf(secs[j]), w: px(w), h: px(ht) })
    }
  })
  const groups = new Map(), walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT)
  for (let n; (n = walker.nextNode());) {
    const el = n.parentElement, t = n.data.trim()
    if (!t || !el || el.closest('script, style, title, noscript, .dd-sr')) continue
    const s = cs(el), isSvg = el instanceof SVGElement, frameEl = isSvg ? el.ownerSVGElement : el
    if (s.visibility === 'hidden' || s.display === 'none') continue
    const rg = document.createRange()
    rg.selectNodeContents(n)
    const cut = !isSvg && s.overflowX !== 'visible' && el.getBoundingClientRect()
    const boxes = (isSvg ? [el.getBoundingClientRect()] : [...rg.getClientRects()]).map(b => !cut ? b
      : DOMRect.fromRect({ x: b.left, y: b.top, width: max(0, min(b.right, cut.right) - b.left), height: b.height })).filter(b => b.width > 0 && b.height > 0)
    if (!boxes.length) continue
    const label = `"${t.slice(0, 40)}" in ${nameOf(secOf(el))}`, size = parseFloat(s.fontSize), fg = rgba(isSvg ? s.fill : s.color)
    if (size < 9) rep.small.push({ text: label, px: size })
    if (fg) {
      const bg = bgOf(frameEl), ratio = contrast(over(fg, bg), bg), need = size >= 24 || (size >= 18.66 && +s.fontWeight >= 700) ? 3 : 4.5
      if (ratio < need) rep.contrast.push({ text: label, ratio, need, color: hex(fg), bg: hex(bg) })
    }
    let out = 0
    for (let a = frameEl; a && a !== body && out <= 1 && !(s.textOverflow === 'ellipsis' && el.title); a = a.parentElement) {
      const o = cs(a)
      if (a !== el.ownerSVGElement && o.overflowX === 'visible' && o.overflowY === 'visible') continue
      const ar = a.getBoundingClientRect()
      out = max(...boxes.map(b => max(ar.left - b.left, b.right - ar.right, ar.top - b.top, b.bottom - ar.bottom)))
    }
    if (!isSvg && s.textOverflow === 'ellipsis' && !el.title && el.scrollWidth > el.clientWidth + 1) out = max(out, el.scrollWidth - el.clientWidth)
    if (out > 1) rep.clipped.push({ text: label, px: px(out) })
    const g = secOf(el) || body
    if (!groups.has(g)) groups.set(g, [])
    groups.get(g).push({ label, boxes })
  }
  for (const list of groups.values()) {
    list.forEach((a, i) => list.slice(i + 1).forEach(b => {
      const hit = a.boxes.some(p => b.boxes.some(q => meet(p, q).every(d => d > 2)))
      if (hit && rep.collide.length < 40) rep.collide.push({ a: a.label, b: b.label })
    }))
  }
  const seen = new Set()
  for (const el of document.querySelectorAll('.dd-mark')) {
    const s = cs(el), c = rgba(s.stroke !== 'none' && parseFloat(s.strokeWidth) > 0 ? s.stroke : s.fill)
    if (!c || !c[3]) continue
    const bg = bgOf(el.ownerSVGElement || el), ratio = contrast(over(c, bg), bg), key = where(el) + hex(c)
    if (ratio < 3 && !seen.has(key)) { seen.add(key); rep.marks.push({ el: where(el), color: hex(c), ratio }) }
  }
  const colors = new Map(), sat = (c, el, prop) => {
    if (!c || !c[3] || chroma(c) < 0.25) return
    const e = colors.get(hex(c)) || { color: hex(c), count: 0, where: `${where(el)} ${prop}` }
    e.count++
    colors.set(hex(c), e)
  }
  for (const el of [body, ...body.querySelectorAll('*')]) {
    if (el.closest('script, style, title')) continue
    const s = cs(el)
    if (el instanceof SVGElement) { sat(rgba(s.fill), el, 'fill'); sat(rgba(s.stroke), el, 'stroke'); continue }
    if ([...el.childNodes].some(n => n.nodeType === 3 && n.data.trim())) sat(rgba(s.color), el, 'color')
    sat(rgba(s.backgroundColor), el, 'background')
    for (const d of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(s[`border${d}Width`]) > 0) sat(rgba(s[`border${d}Color`]), el, 'border')
  }
  rep.colors = [...colors.values()]
  rep.empty = [...document.querySelectorAll('.dd-mount')].filter(el => !el.querySelector('svg, table') && !el.textContent.trim()).map(where)
  rep.rows = dd.flagged()
  try {
    const d = JSON.parse((document.getElementById('dd-data') || {}).textContent || '{}')
    rep.asOf = d.asOf || null
    for (const [k, m] of Object.entries(d.measures || {})) {
      if (!['target', 'forecast', 'prior', 'norm', 'ranges'].some(f => m[f] != null)) rep.noComparison.push(m.label || k)
    }
  } catch (err) { errors.push('dd-data: ' + err.message) }
  const out = document.getElementById('dd-report') || body.appendChild(Object.assign(document.createElement('script'), { type: 'application/json', id: 'dd-report' }))
  out.textContent = JSON.stringify(rep).replace(/</g, '\\u003c')
}

addEventListener('load', () => document.fonts.ready.then(check))
})()
