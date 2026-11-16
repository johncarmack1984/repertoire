"""Rebuild plugins/data-dashboard/tests/components.html: `new --data`, then splice in the page regions."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = REPO / "plugins/data-dashboard/tests/components.html"
SCRIPT = REPO / "plugins/data-dashboard/skills/data-dashboard/scripts/dashboard.py"

STYLE = """<style>
:root { --dd-cols: 72; --dd-rows: 55; }
.dd-grid { grid-template-columns: 26fr 22fr 18fr; }
.cmp-now { margin-left: auto; display: flex; flex-wrap: wrap; gap: 0 calc(var(--u) * 1.5); }
.cmp-icons span + span { margin-left: 0.25em; }
.cmp-icons { margin-right: calc(var(--u) * 1); }
</style>"""


def sec(id_, title, qual="", legend=False, body=None):
    q = f' <span class="dd-qual">({qual})</span>' if qual else ""
    lg = f'<span class="dd-legend" id="{id_}-legend"></span>' if legend else ""
    return f'<section class="dd-sec">\n<h2 class="dd-sec-title">{title}{q}{lg}</h2>\n{body or f"<div id={chr(34)}{id_}{chr(34)}></div>"}\n</section>'


PAGE = f"""<header class="dd-head">
<h1 class="dd-title">Components</h1>
<p class="dd-asof" id="dd-asof"></p>
<p class="dd-flags" id="dd-flags"></p>
<div class="cmp-now"><div id="spark-defects"></div><div id="spark-mtd"></div></div>
</header>
<main class="dd-grid">
<div class="dd-stack">
{sec("key", "Key metrics", "QTD vs. target", legend=True)}
{sec("own", "Own scales", "each row on its own scale")}
{sec("shared", "Shared scale", "days of supply; targets differ, no alerts")}
{sec("netnew", "Net new accounts", "by month, zero and negative")}
</div>
<div class="dd-stack">
{sec("bul", "Bullet graphs", legend=True)}
{sec("regions", "Revenue by region", "YTD vs. target, % of total")}
{sec("pipe", "Revenue QTD", "actual and pipeline vs. target, $K")}
{sec("cust", "Top customers", "by pipeline")}
{sec("states", "Revenue by state", "area is revenue, color is % of quota", legend=True)}
</div>
<div class="dd-stack">
{sec("traffic", "Network traffic", "kilobytes by hour")}
{sec("visitors", "Visitors", "vs. same month last year")}
{sec("resp", "Response time and salary", "box plots; range bars", body='<div id="resp"></div>' + chr(10) + '<div id="sal"></div>')}
{sec("ads", "Radio ads and sales", "monthly, $K")}
</div>
</main>
<footer class="dd-foot"><span class="cmp-icons"><span id="i-warn"></span> warning <span id="i-alert"></span> critical <span id="i-up"></span> up <span id="i-down"></span> down, bad <span id="i-check"></span> check <span id="i-x"></span> x <span id="i-ast"></span> asterisk</span>
Edge cases: a value past the scale, zero and negative values, lower-is-better measures, missing and one-point history, a scale that doesn't start at zero, a table with no alerts, long labels, a measure with its own policy (on-time delivery), a header wider than its labels, digits that set wider than they measure ($111,111), treemap cells too small for their labels.</footer>
<script type="application/json" id="dd-data">
@DATA@
</script>
<script type="module">
const dd = DataDashboard
const d = dd.data()
const m = d.measures
document.querySelector('#dd-asof').textContent = `Data as of ${{dd.asOf(d.asOf, d.tz, d.locale)}}`
dd.flags('#dd-flags')
dd.legend('#key-legend', [{{ mark: 'bar', label: 'Actual' }}, {{ mark: 'target', label: 'Target' }}, {{ mark: 'band', tone: 1, label: '<85%' }}, {{ mark: 'band', tone: 2, label: '85-95%' }}, {{ mark: 'band', tone: 4, label: '95%+' }}])
const lined = {{ labelWidth: 7, valueWidth: 3.5 }}
dd.table('#key', m, {{ rows: ['revenue', 'profit', 'orderSize', 'onTime', 'expenses', 'newCustomers'], domain: [0, 1.5], ...lined,
  head: {{ spark: 'Past 12 months', label: 'Metric', graph: '% of target', value: 'Actual' }} }})
dd.table('#own', m, {{ rows: ['availability', 'backlog', 'margin'], scale: 'own', ...lined }})
dd.table('#shared', m, {{ rows: ['reno', 'joliet', 'fresno'], scale: 'shared',
  head: {{ spark: 'Past 14 days', label: 'Distribution center', graph: 'Days of supply', value: 'Days' }} }})
dd.bars('#netnew', d.netNew, {{ orient: 'v', height: 4.5 }})
dd.spark('#spark-defects', d.defects)
dd.spark('#spark-mtd', d.mtd)
dd.alert('#i-warn', 'warn')
dd.alert('#i-alert', 'alert')
dd.trend('#i-up', 'up')
dd.trend('#i-down', 'down', {{ bad: true }})
dd.mark('#i-check', 'check')
dd.mark('#i-x', 'x')
dd.mark('#i-ast', 'asterisk')
dd.bullet('#bul', [m.revenue, m.availability])
dd.legend('#bul-legend', [{{ mark: 'bar', label: 'Actual' }}, {{ mark: 'projection', label: 'Projected' }}, {{ mark: 'target', label: 'Target' }}])
dd.bars('#regions', d.regions, {{ format: 'usd0k', pctTotal: true }})
dd.stacked('#pipe', d.pipeline, {{ parts: ['actual', 'pipeline'], format: 'usd0k', alertWhen: 'sumBelowTarget' }})
dd.line('#traffic', d.traffic, {{ height: 5 }})
dd.line('#visitors', d.visitors, {{ deviation: true, refLabel: 'Last year', height: 4 }})
dd.box('#resp', d.response, {{ format: 'dec1' }})
dd.box('#sal', d.salaries, {{ range: true, format: 'usd0k' }})
dd.scatter('#ads', d.ads, {{ formatX: 'dec1', formatY: 'dec1', labels: true, xLabel: 'Radio ads, $K', yLabel: 'Revenue, $K', height: 5.5 }})
dd.treemap('#states', d.states, {{ height: 9 }})
dd.legend('#states-legend', [{{ mark: 'heat', tone: 0, label: 'Quota met' }}, {{ mark: 'heat', tone: 3, label: 'Short' }}, {{ mark: 'heat', tone: 'a', label: 'Under 85%' }}])
dd.text('#cust', d.customers, {{ rank: true, cols: ['name::Customer', 'pipeline:usd0k:Pipeline', 'qtd:usd0k:QTD', 'ytd:usd0k:YTD'] }})
</script>"""


def main():
    data = (HERE / "components.data.json").read_text().strip()
    subprocess.run([sys.executable, SCRIPT, "new", OUT, "--force", "--title", "Components", "--viewport", "1440x1100", "--data", HERE / "components.data.json"], check=True)
    text = OUT.read_text()
    text = re.sub(r"(<!-- data-dashboard:page-style -->\n).*?(\n<!-- /data-dashboard:page-style -->)", lambda m: m[1] + STYLE + m[2], text, flags=re.S)
    page = PAGE.replace("@DATA@", data.replace("</", "<\\/"))
    text = re.sub(r"(<!-- data-dashboard:page -->\n).*?(\n<!-- /data-dashboard:page -->)", lambda m: m[1] + page + m[2], text, flags=re.S)
    OUT.write_text(text)
    print(f"built {OUT}")


main()
