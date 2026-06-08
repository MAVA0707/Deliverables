"""Build the HTML dashboard for Chleo."""
import json
from pathlib import Path

DATA = json.loads(Path("/home/claude/dashboard_data.json").read_text())

# Format helpers
def fmt_money(v, unit='M'):
    if unit == 'M':
        return f"${v/1e6:.1f}M"
    if unit == 'K':
        return f"${v/1e3:.0f}K"
    return f"${v:,.0f}"

def fmt_pct(v, d=0):
    return f"{v:.{d}f}%"

# === Build chart data as JS objects ===

# Chart 1: Tenure buckets
tenure_labels = [b['label'] for b in DATA['tenure_buckets']]
tenure_counts = [b['count'] for b in DATA['tenure_buckets']]
tenure_pcts = [b['pct'] for b in DATA['tenure_buckets']]

# Chart 2: Monthly churn time series
monthly_x = [m['month'] for m in DATA['monthly_churn']]
monthly_y = [m['count'] for m in DATA['monthly_churn']]

# Chart 3: Industry rate
ind_data = sorted(DATA['by_industry'], key=lambda r: r['rate'], reverse=True)
ind_names = [r['industry'] for r in ind_data]
ind_rates = [r['rate'] for r in ind_data]
ind_arr_lost = [r['arr_amount']/1e6 for r in ind_data]

# Chart 4: Reasons
reason_data = DATA['reasons']
reason_names = [r['reason'].title() for r in reason_data]
reason_counts = [r['count'] for r in reason_data]

# Chart 5: Reason by industry stacked
rxi = DATA['reason_by_industry']

# Embed data as JSON string
data_js = json.dumps({
    'tenure': {'labels': tenure_labels, 'counts': tenure_counts, 'pcts': tenure_pcts},
    'monthly': {'x': monthly_x, 'y': monthly_y},
    'industry': {'names': ind_names, 'rates': ind_rates, 'arr': ind_arr_lost},
    'reasons': {'names': reason_names, 'counts': reason_counts},
    'rxi': rxi
})

kpi = DATA['kpi']

# === HTML ===

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Churn Evidence — Ravenstack</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js" onerror="console.log('CDN blocked, using inline fallback')"></script>
<script>__PLOTLY_INLINE__</script>
<style>
:root {{
  --navy: #1F4E79;
  --navy-dark: #163A5A;
  --navy-light: #2E74B5;
  --ink: #1A1A1A;
  --ink-soft: #4A4A4A;
  --rule: #D8D2C5;
  --paper: #FAF8F3;
  --paper-tint: #F0EDE4;
  --warning: #B23A48;
  --warning-soft: #E8D6D8;
  --success: #4F7942;
  --success-soft: #DAE3CF;
  --muted: #8B7E6A;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'IBM Plex Sans', -apple-system, sans-serif;
  background: var(--paper);
  color: var(--ink);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}}

.page {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 64px 56px 96px;
}}

/* === Header === */
.masthead {{
  border-bottom: 1px solid var(--rule);
  padding-bottom: 40px;
  margin-bottom: 56px;
}}
.eyebrow {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 16px;
}}
h1.title {{
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 56px;
  font-weight: 600;
  line-height: 1.05;
  color: var(--ink);
  letter-spacing: -0.02em;
  margin-bottom: 20px;
  max-width: 850px;
}}
h1.title em {{
  font-style: italic;
  color: var(--navy);
  font-weight: 500;
}}
.deck {{
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 22px;
  line-height: 1.45;
  color: var(--ink-soft);
  font-weight: 400;
  max-width: 720px;
}}
.byline {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: var(--muted);
  margin-top: 28px;
  letter-spacing: 0.04em;
}}

/* === Section heading === */
section {{
  margin-bottom: 64px;
}}
.section-head {{
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 8px;
  border-top: 2px solid var(--ink);
  padding-top: 20px;
}}
.section-number {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.15em;
  color: var(--navy);
}}
.section-head h2 {{
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--ink);
}}
.section-deck {{
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 18px;
  line-height: 1.5;
  color: var(--ink-soft);
  max-width: 720px;
  margin-bottom: 32px;
}}

/* === KPI Grid === */
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border: 1px solid var(--rule);
  background: white;
}}
.kpi {{
  padding: 28px 24px;
  border-right: 1px solid var(--rule);
}}
.kpi:last-child {{ border-right: none; }}
.kpi-label {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 14px;
  font-weight: 500;
}}
.kpi-value {{
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 44px;
  font-weight: 600;
  line-height: 1;
  color: var(--ink);
  letter-spacing: -0.02em;
}}
.kpi-value.warn {{ color: var(--warning); }}
.kpi-detail {{
  font-size: 13px;
  color: var(--ink-soft);
  margin-top: 10px;
  line-height: 1.4;
}}

/* === Chart layouts === */
.two-col {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-top: 8px;
}}
.chart-card {{
  background: white;
  border: 1px solid var(--rule);
  padding: 28px;
}}
.chart-card.full {{ width: 100%; }}
.chart-title {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: var(--ink);
  text-transform: uppercase;
  margin-bottom: 4px;
}}
.chart-subtitle {{
  font-family: 'Crimson Pro', serif;
  font-size: 15px;
  font-style: italic;
  color: var(--ink-soft);
  margin-bottom: 20px;
}}
.chart-container {{
  width: 100%;
  height: 320px;
}}

/* === Insight callout === */
.insight {{
  background: var(--paper-tint);
  border-left: 3px solid var(--navy);
  padding: 20px 24px;
  margin-top: 24px;
  font-family: 'Crimson Pro', serif;
  font-size: 17px;
  line-height: 1.55;
  color: var(--ink);
}}
.insight strong {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-weight: 600;
  font-size: 11px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--navy);
  display: block;
  margin-bottom: 8px;
}}

/* === Signal table === */
.signal-table {{
  border: 1px solid var(--rule);
  background: white;
}}
.signal-row {{
  display: grid;
  grid-template-columns: 220px 100px 1fr;
  gap: 24px;
  padding: 22px 28px;
  border-bottom: 1px solid var(--rule);
  align-items: start;
}}
.signal-row:last-child {{ border-bottom: none; }}
.signal-row.head {{
  background: var(--ink);
  color: white;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 16px 28px;
  font-weight: 500;
}}
.signal-name {{
  font-family: 'Crimson Pro', serif;
  font-size: 18px;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.3;
}}
.signal-strength {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 6px 10px;
  display: inline-block;
  font-weight: 500;
  text-align: center;
}}
.signal-strength.strong {{ background: var(--success-soft); color: var(--success); }}
.signal-strength.moderate {{ background: #F3E8C5; color: #6B5318; }}
.signal-strength.weak {{ background: var(--warning-soft); color: var(--warning); }}
.signal-finding {{
  font-size: 14px;
  color: var(--ink);
  margin-bottom: 6px;
  font-weight: 500;
}}
.signal-note {{
  font-size: 13px;
  color: var(--ink-soft);
  font-family: 'Crimson Pro', serif;
  font-style: italic;
  line-height: 1.5;
}}

/* === Action callout === */
.action {{
  background: var(--ink);
  color: var(--paper);
  padding: 40px 48px;
  margin-top: 48px;
}}
.action-eyebrow {{
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(250, 248, 243, 0.6);
  margin-bottom: 16px;
}}
.action h3 {{
  font-family: 'Crimson Pro', serif;
  font-size: 32px;
  font-weight: 500;
  line-height: 1.2;
  margin-bottom: 20px;
  letter-spacing: -0.01em;
}}
.action p {{
  font-family: 'Crimson Pro', serif;
  font-size: 18px;
  line-height: 1.55;
  color: rgba(250, 248, 243, 0.85);
  max-width: 750px;
  margin-bottom: 16px;
}}
.action p:last-child {{ margin-bottom: 0; }}

/* === Footer === */
footer {{
  margin-top: 80px;
  padding-top: 32px;
  border-top: 1px solid var(--rule);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 0.04em;
  line-height: 1.7;
}}
footer strong {{ color: var(--ink); font-weight: 500; }}

@media print {{
  body {{ background: white; }}
  .chart-card, .kpi-grid, .signal-table {{ break-inside: avoid; }}
  section {{ break-inside: avoid; }}
}}
</style>
</head>
<body>
<div class="page">

<!-- Masthead -->
<header class="masthead">
  <div class="eyebrow">Evidence Report · Prepared for the CEO</div>
  <h1 class="title">Where churn happens at <em>Ravenstack</em></h1>
  <p class="deck">A read of two years of customer, subscription, usage, and support data, focused on one question: what does the data actually show, and what is it silent on?</p>
  <p class="byline">Markus von Aschoff · markus@vonaschoff.de · June 2026</p>
</header>

<!-- Section 1: Headlines -->
<section>
  <div class="section-head">
    <span class="section-number">01</span>
    <h2>The headlines</h2>
  </div>
  <p class="section-deck">Four numbers to anchor the conversation. The first is what churn has already cost. The second is what we project will be at risk in the next year if patterns continue.</p>
  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-label">Lost ARR · Lifetime</div>
      <div class="kpi-value warn">{fmt_money(kpi['lost_arr_lifetime'])}</div>
      <div class="kpi-detail">Total annualised revenue from cancelled subscriptions across 2023 and 2024.</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">ARR at risk · Next 12 mo</div>
      <div class="kpi-value warn">{fmt_money(kpi['annual_at_risk_arr'])}</div>
      <div class="kpi-detail">Applying the 4% monthly SMB SaaS churn benchmark to current active ARR of {fmt_money(kpi['active_arr'])}.</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Annual Churn Rate</div>
      <div class="kpi-value">{fmt_pct(kpi['annual_churn_rate'], 1)}</div>
      <div class="kpi-detail">Annualised from lifetime cancellation over the 2-year observation window.</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Accounts Churned</div>
      <div class="kpi-value">{kpi['n_churned']} <span style="font-size:24px; color:var(--muted)">/ {kpi['n_total']}</span></div>
      <div class="kpi-detail">{fmt_pct(kpi['churn_rate_lifetime'], 1)} of all customers have left since January 2023.</div>
    </div>
  </div>
</section>

<!-- Section 2: When does churn happen -->
<section>
  <div class="section-head">
    <span class="section-number">02</span>
    <h2>When does churn happen?</h2>
  </div>
  <p class="section-deck">Tenure at the moment of cancellation, and the monthly count of churn events. Most customers who leave do so very early.</p>
  <div class="two-col">
    <div class="chart-card">
      <div class="chart-title">Tenure at first cancellation</div>
      <div class="chart-subtitle">Days from signup to first churn event, by bucket</div>
      <div class="chart-container" id="chart-tenure"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Monthly churn events</div>
      <div class="chart-subtitle">All cancellation events recorded each month, 2023-2024</div>
      <div class="chart-container" id="chart-monthly"></div>
    </div>
  </div>
  <div class="insight">
    <strong>What this means</strong>
    {DATA['pct_first_90']:.0f}% of all churn happens in the first 90 days after signup. This matches the published B2B SaaS benchmark of 70% (Optifai 2026, 939 companies). The single highest-leverage intervention is improving onboarding for new accounts. A model that flags at-risk customers must weight tenure heavily.
  </div>
</section>

<!-- Section 3: Where does churn concentrate -->
<section>
  <div class="section-head">
    <span class="section-number">03</span>
    <h2>Where does churn concentrate?</h2>
  </div>
  <p class="section-deck">Two views of the same data: rate of churn (left) and absolute dollars lost (right). The two do not point at the same segment.</p>
  <div class="two-col">
    <div class="chart-card">
      <div class="chart-title">Churn rate by industry</div>
      <div class="chart-subtitle">Share of customers in each industry who have churned</div>
      <div class="chart-container" id="chart-industry-rate"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Lost ARR by industry</div>
      <div class="chart-subtitle">Lifetime annualised revenue from cancellations</div>
      <div class="chart-container" id="chart-industry-arr"></div>
    </div>
  </div>
  <div class="insight">
    <strong>What this means</strong>
    DevTools churns at the highest rate (31%), nearly 2x the lowest (Cybersecurity at 16%). But Cybersecurity loses the most dollars overall because of higher account value. The implication: a retention play for DevTools fixes the highest churn rate, while a retention play for Cybersecurity protects the most revenue. They are different programs.
  </div>
</section>

<!-- Section 4: Why -->
<section>
  <div class="section-head">
    <span class="section-number">04</span>
    <h2>Why customers say they leave</h2>
  </div>
  <p class="section-deck">Self-reported cancellation reasons. These come from the exit survey and are imperfect (customers under-report price sensitivity, for instance), but the distribution is informative.</p>
  <div class="two-col">
    <div class="chart-card">
      <div class="chart-title">Reasons for cancellation</div>
      <div class="chart-subtitle">All 600 churn events, 2023-2024</div>
      <div class="chart-container" id="chart-reasons"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Reasons by industry</div>
      <div class="chart-subtitle">Same data, segmented by customer industry</div>
      <div class="chart-container" id="chart-rxi"></div>
    </div>
  </div>
  <div class="insight">
    <strong>What this means</strong>
    "Features" and "support" together drive 36% of stated churn. Both are addressable, but by different teams (product vs. customer success). Note that "unknown" accounts for 16% of cancellations - improving exit survey response is worth doing on its own.
  </div>
</section>

<!-- Section 5: The signal -->
<section>
  <div class="section-head">
    <span class="section-number">05</span>
    <h2>What can we actually predict?</h2>
  </div>
  <p class="section-deck">An honest test of which signals in this data would be useful for early warning. Some are strong. Two often-assumed signals are weak.</p>

  <div class="signal-table">
    <div class="signal-row head">
      <div>Signal</div>
      <div>Strength</div>
      <div>What the data shows</div>
    </div>
"""

# Signal rows
for sig in DATA['signals']:
    strength_class = sig['strength']
    strength_label = sig['strength'].upper()
    html += f"""    <div class="signal-row">
      <div class="signal-name">{sig['name']}</div>
      <div><span class="signal-strength {strength_class}">{strength_label}</span></div>
      <div>
        <div class="signal-finding">{sig['finding']}</div>
        <div class="signal-note">{sig['note']}</div>
      </div>
    </div>
"""

html += """  </div>

  <div class="insight">
    <strong>Implication for the proposal</strong>
    The two strong signals (tenure and industry) work for a simple rule-based health score on day one. The two weak signals (usage drop, ticket spike) mean the ML model cannot rely on them alone. This is exactly the Phase 1 data audit that the proposal called for, and it argues for the rule-based fallback being the realistic starting point.
  </div>
</section>

<!-- Section 6: Action -->
<div class="action">
  <div class="action-eyebrow">What to do with this</div>
  <h3>Start with new accounts in DevTools. That's where the loss is.</h3>
  <p>The data points to one concrete intervention before any ML work: a structured 90-day onboarding programme for new accounts, with DevTools customers prioritised. This costs nothing to start, addresses the segment where the strongest signals concentrate, and produces the training data the model needs in Phase 2.</p>
  <p>The fuller plan, costs, and timeline are in the main proposal. This dashboard is the evidence behind that plan.</p>
</div>

<!-- Footer -->
<footer>
  <strong>Data source.</strong> 500 customer accounts, 4,514 active subscriptions, 600 churn events, 25,000 feature usage records, and 2,000 support tickets, covering January 2023 to December 2024.<br>
  <strong>Methodology.</strong> Tenure is the days between signup_date and first churn_date per account. Annual churn rate is annualised from lifetime cancellation over the 2-year window. ARR-at-risk uses the 4% monthly SMB SaaS benchmark from Optifai 2026 applied to current active ARR. Signal strength is qualitative based on the size of the difference between churned and retained populations.<br>
  <strong>Caveats.</strong> This dataset describes a customer base larger than the 10-to-50-person company framing in the proposal. The patterns, not the totals, are what generalise. The "usage drop before churn" signal is weaker here than typical real-world SaaS data; the Phase 1 audit will re-test this on production data before committing to an ML approach.
</footer>

</div>

<script>
const D = """ + data_js + """;

const COLOR = {
  navy: '#1F4E79',
  navyDark: '#163A5A',
  navyLight: '#2E74B5',
  ink: '#1A1A1A',
  inkSoft: '#4A4A4A',
  warning: '#B23A48',
  warningSoft: '#E8D6D8',
  success: '#4F7942',
  rule: '#D8D2C5',
  paper: '#FAF8F3',
  muted: '#8B7E6A'
};

const FONT_BODY = "'IBM Plex Sans', sans-serif";
const FONT_NUM = "'IBM Plex Mono', monospace";

const baseLayout = {
  font: { family: FONT_BODY, size: 12, color: COLOR.ink },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  margin: { l: 60, r: 20, t: 10, b: 50 },
  xaxis: {
    showgrid: false,
    showline: true,
    linecolor: COLOR.rule,
    linewidth: 1,
    ticks: 'outside',
    tickcolor: COLOR.rule,
    ticklen: 4,
    tickfont: { family: FONT_NUM, size: 10, color: COLOR.inkSoft }
  },
  yaxis: {
    showgrid: true,
    gridcolor: COLOR.rule,
    gridwidth: 0.5,
    zeroline: false,
    tickfont: { family: FONT_NUM, size: 10, color: COLOR.inkSoft }
  }
};

const config = { displayModeBar: false, responsive: true };

// === Chart 1: Tenure histogram ===
Plotly.newPlot('chart-tenure', [{
  x: D.tenure.labels,
  y: D.tenure.pcts,
  type: 'bar',
  marker: {
    color: D.tenure.labels.map((l, i) => i < 2 ? COLOR.warning : COLOR.navy)
  },
  text: D.tenure.pcts.map(p => p.toFixed(0) + '%'),
  textposition: 'outside',
  textfont: { family: FONT_NUM, size: 11, color: COLOR.ink },
  hovertemplate: '<b>%{x}</b><br>%{y:.1f}% of churned accounts<br>%{customdata} accounts<extra></extra>',
  customdata: D.tenure.counts,
  cliponaxis: false
}], {
  ...baseLayout,
  yaxis: { ...baseLayout.yaxis, ticksuffix: '%', range: [0, Math.max(...D.tenure.pcts) * 1.25] },
  margin: { l: 50, r: 20, t: 20, b: 60 }
}, config);

// === Chart 2: Monthly churn ===
Plotly.newPlot('chart-monthly', [{
  x: D.monthly.x,
  y: D.monthly.y,
  type: 'scatter',
  mode: 'lines',
  line: { color: COLOR.navy, width: 2, shape: 'spline', smoothing: 0.5 },
  fill: 'tozeroy',
  fillcolor: 'rgba(31, 78, 121, 0.08)',
  hovertemplate: '<b>%{x}</b><br>%{y} churn events<extra></extra>'
}], {
  ...baseLayout,
  margin: { l: 50, r: 20, t: 20, b: 50 },
  xaxis: {
    ...baseLayout.xaxis,
    type: 'date',
    tickformat: '%b<br>%Y',
    dtick: 'M3',
    tickangle: 0
  }
}, config);

// === Chart 3: Industry rate ===
Plotly.newPlot('chart-industry-rate', [{
  x: D.industry.rates,
  y: D.industry.names,
  type: 'bar',
  orientation: 'h',
  marker: {
    color: D.industry.names.map((n, i) => i === 0 ? COLOR.warning : COLOR.navy)
  },
  text: D.industry.rates.map(r => r.toFixed(0) + '%'),
  textposition: 'outside',
  textfont: { family: FONT_NUM, size: 11, color: COLOR.ink },
  hovertemplate: '<b>%{y}</b><br>%{x:.1f}% churn rate<extra></extra>',
  cliponaxis: false
}], {
  ...baseLayout,
  margin: { l: 110, r: 50, t: 20, b: 40 },
  xaxis: {
    ...baseLayout.xaxis,
    type: 'linear',
    ticksuffix: '%',
    range: [0, Math.max(...D.industry.rates) * 1.2]
  },
  yaxis: { ...baseLayout.yaxis, showgrid: false, type: 'category', autorange: 'reversed' }
}, config);

// === Chart 4: Industry ARR lost ===
const arrSorted = D.industry.names.map((n, i) => ({ name: n, val: D.industry.arr[i] }))
                                   .sort((a, b) => b.val - a.val);
Plotly.newPlot('chart-industry-arr', [{
  x: arrSorted.map(d => d.val),
  y: arrSorted.map(d => d.name),
  type: 'bar',
  orientation: 'h',
  marker: { color: COLOR.navy },
  text: arrSorted.map(d => '$' + d.val.toFixed(1) + 'M'),
  textposition: 'outside',
  textfont: { family: FONT_NUM, size: 11, color: COLOR.ink },
  hovertemplate: '<b>%{y}</b><br>$%{x:.2f}M lost ARR<extra></extra>',
  cliponaxis: false
}], {
  ...baseLayout,
  margin: { l: 110, r: 60, t: 20, b: 40 },
  xaxis: {
    ...baseLayout.xaxis,
    type: 'linear',
    tickprefix: '$',
    ticksuffix: 'M',
    range: [0, Math.max(...arrSorted.map(d => d.val)) * 1.2]
  },
  yaxis: { ...baseLayout.yaxis, showgrid: false, type: 'category', autorange: 'reversed' }
}, config);

// === Chart 5: Reasons ===
Plotly.newPlot('chart-reasons', [{
  x: D.reasons.names,
  y: D.reasons.counts,
  type: 'bar',
  marker: { color: COLOR.navy },
  text: D.reasons.counts,
  textposition: 'outside',
  textfont: { family: FONT_NUM, size: 11, color: COLOR.ink },
  hovertemplate: '<b>%{x}</b><br>%{y} events<extra></extra>',
  cliponaxis: false
}], {
  ...baseLayout,
  margin: { l: 50, r: 20, t: 20, b: 50 },
  yaxis: { ...baseLayout.yaxis, range: [0, Math.max(...D.reasons.counts) * 1.2] }
}, config);

// === Chart 6: Reasons by industry stacked ===
const reasonColors = {
  features: COLOR.navy,
  support: COLOR.navyLight,
  budget: '#8FA9C0',
  pricing: '#B8C7D6',
  competitor: '#7C8B6F',
  unknown: COLOR.muted
};
const rxiTraces = D.rxi.reasons.map((reason, idx) => ({
  x: D.rxi.industries,
  y: D.rxi.data.map(row => row[idx]),
  name: reason.charAt(0).toUpperCase() + reason.slice(1),
  type: 'bar',
  marker: { color: reasonColors[reason] || COLOR.muted },
  hovertemplate: '<b>%{x}</b><br>' + reason + ': %{y}<extra></extra>'
}));
Plotly.newPlot('chart-rxi', rxiTraces, {
  ...baseLayout,
  barmode: 'stack',
  margin: { l: 50, r: 20, t: 20, b: 60 },
  legend: {
    orientation: 'h',
    y: -0.25,
    x: 0,
    font: { family: FONT_BODY, size: 10, color: COLOR.inkSoft }
  }
}, config);
</script>
</body>
</html>
"""

Path("/home/claude/churn_dashboard.html").write_text(html)
print(f"Wrote dashboard: {len(html):,} bytes")

# Inline Plotly so the dashboard works offline
plotly_src = Path("/home/claude/plotly.min.js").read_text()
final_html = html.replace("__PLOTLY_INLINE__", plotly_src)
Path("/home/claude/churn_dashboard.html").write_text(final_html)
print(f"Final dashboard with inlined Plotly: {len(final_html):,} bytes")
