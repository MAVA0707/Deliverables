"""
eval_dashboard_plotly.py — the Week 7 · Day 5 example *evaluation dashboard*, in pure Plotly.

Run it:
    python eval_dashboard_plotly.py
    # writes eval_dashboard.html (open in a browser); also eval_dashboard.png if kaleido is present

Each panel deliberately applies the data-viz principles from the morning lesson:
  • One chart, one message — every panel makes a single, falsifiable point.
  • Headline titles — the title states the conclusion, not the axes.
  • Color the signal, gray the noise — only the bar/point that makes the point is colored.
  • Reference lines — a target line the value either clears or doesn't.
  • Right chart for the question — bar (comparison), line (trend), histogram (distribution).
  • Show "what" and "so what", not statistical method — no p-values, no dual axes, no 3D.
This is the teaching contrast to the Tableau/PowerBI lab: the same dashboard, as code.
"""
from __future__ import annotations
import pathlib
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import eval_data as ed

# --- palette (matches the board's semantic colors) ---------------------------
INK = "#1e1e1e"; MUTE = "#868e96"; GRID = "#e9ecef"
SIGNAL = "#e03131"   # red — the thing that needs attention
GOOD = "#2f9e44"     # green
BLUE = "#1971c2"
TARGET = 7.0         # the judge-score bar every category should clear
PAPER = "#ffffff"

df = ed.load_eval()
cat = ed.by_category(df)          # sorted ascending by avg_score
wk = ed.weekly_trend(df)
k = ed.kpis(df)
worst = cat.iloc[0]["category"]   # the category to call out (lowest avg score)
_n_below = int((cat["avg_score"] < TARGET).sum())
_below_phrase = ("the only category below" if _n_below == 1
                 else f"worst of {_n_below} below")
BAR_HEADLINE = (f"<b>{worst.replace('_', ' ').title()} drags the model down</b> — "
                f"{cat.iloc[0]['avg_score']:.1f}/10, {_below_phrase} the {TARGET:.0f} target")


def _kpi(value, label, good=True, suffix="", prefix=""):
    return go.Indicator(
        mode="number", value=value,
        number={"suffix": suffix, "prefix": prefix, "font": {"size": 40,
                "color": GOOD if good else SIGNAL}},
        title={"text": f"<span style='font-size:13px;color:{MUTE}'>{label}</span>"},
    )


def _vline(fig, xref, x, color, text=None, dash="dash", width=2):
    """Vertical reference line across a subplot (avoids add_vline's indicator bug)."""
    ydom = ("y" if xref == "x" else "y" + xref[1:]) + " domain"
    fig.add_shape(type="line", xref=xref, yref=ydom, x0=x, x1=x, y0=0, y1=1,
                  line=dict(color=color, dash=dash, width=width))
    if text:
        # place INSIDE the panel (just under the title) so it never collides
        fig.add_annotation(xref=xref, yref=ydom, x=x, y=0.96, text=text,
                           showarrow=False, font=dict(size=11, color=color),
                           yanchor="top", xanchor="left", bgcolor="rgba(255,255,255,0.7)")


def _hline(fig, yref, y, color, dash="dot", width=1.5):
    xdom = ("x" if yref == "y" else "x" + yref[1:]) + " domain"
    fig.add_shape(type="line", yref=yref, xref=xdom, y0=y, y1=y, x0=0, x1=1,
                  line=dict(color=color, dash=dash, width=width))


def build_figure() -> go.Figure:
    fig = make_subplots(
        rows=3, cols=4,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"},
             {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy", "colspan": 2}, None],
        ],
        row_heights=[0.16, 0.42, 0.42],
        vertical_spacing=0.13, horizontal_spacing=0.08,
        subplot_titles=(
            "", "", "", "",
            BAR_HEADLINE,
            "<b>Scores stepped down after Oct 1</b> — a quiet prompt edit shifted the judge baseline",
            "<b>Most tickets score well, but a low-score tail persists</b> — the billing cluster",
            "<b>Accuracy tracks the judge score</b> — billing is weakest on both",
        ),
    )

    # KPI row (Layer-3 business metrics)
    fig.add_trace(_kpi(k["avg_score"], "Avg judge score (/10)",
                       good=k["avg_score"] >= TARGET), 1, 1)
    fig.add_trace(_kpi(k["accuracy"], "Category accuracy", good=k["accuracy"] >= 80,
                       suffix="%"), 1, 2)
    fig.add_trace(_kpi(k["cost_per_run"], "Avg cost / ticket", good=True,
                       prefix="$"), 1, 3)
    fig.add_trace(_kpi(k["p95_latency"], "P95 latency", good=k["p95_latency"] <= 2.5,
                       suffix=" s"), 1, 4)

    # Panel 1 — score by category (horizontal bar; color the signal, gray the rest)
    colors = [SIGNAL if c == worst else MUTE for c in cat["category"]]
    fig.add_trace(go.Bar(
        y=cat["category"], x=cat["avg_score"], orientation="h",
        marker_color=colors, text=[f"{v:.1f}" for v in cat["avg_score"]],
        textposition="outside", cliponaxis=False, hoverinfo="skip"), 2, 1)
    _vline(fig, "x", TARGET, INK, text=f"target {TARGET:.0f}")
    fig.update_xaxes(range=[0, 10], row=2, col=1)

    # Panel 2 — weekly trend (line) with the drift annotation
    fig.add_trace(go.Scatter(
        x=wk["week"], y=wk["avg_score"], mode="lines+markers",
        line=dict(color=BLUE, width=3), marker=dict(size=6), hoverinfo="skip"), 2, 3)
    _hline(fig, "y2", TARGET, MUTE)
    _vline(fig, "x2", ed.DRIFT_WEEK.strftime("%Y-%m-%d"), SIGNAL, text="prompt edited")
    fig.update_yaxes(range=[0, 10], row=2, col=3)

    # Panel 3 — score distribution (histogram)
    fig.add_trace(go.Histogram(
        x=df["judge_score"], nbinsx=20, marker_color=BLUE,
        marker_line_color="white", marker_line_width=0.5, hoverinfo="skip"), 3, 1)
    _vline(fig, "x3", TARGET, INK, text=f"target {TARGET:.0f}")
    fig.update_xaxes(range=[0, 10], title_text="judge score", row=3, col=1)

    # Panel 4 — accuracy by category (bar; same worst-category highlight)
    cat_acc = cat.sort_values("accuracy")
    acolors = [SIGNAL if c == worst else GOOD for c in cat_acc["category"]]
    fig.add_trace(go.Bar(
        y=cat_acc["category"], x=cat_acc["accuracy"], orientation="h",
        marker_color=acolors, text=[f"{v:.0f}%" for v in cat_acc["accuracy"]],
        textposition="outside", cliponaxis=False, hoverinfo="skip"), 3, 3)
    _vline(fig, "x4", 80, INK, text="80%")
    fig.update_xaxes(range=[0, 100], title_text="accuracy %", row=3, col=3)

    # global styling — minimal chrome, high data-ink ratio
    fig.update_layout(
        template="plotly_white", paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        showlegend=False, bargap=0.25, height=900, width=1500,
        margin=dict(l=70, r=40, t=120, b=60),
        title=dict(
            text="<b>Support-Ticket Scoring — Evaluation Dashboard</b><br>"
                 f"<span style='font-size:13px;color:{MUTE}'>"
                 f"{ed.RUN_META['model']} · {ed.RUN_META['prompt']} · judge {ed.RUN_META['judge']} · "
                 f"n={k['n']} tickets &nbsp;|&nbsp; SO WHAT: fix billing first — it fails accuracy AND score</span>",
            x=0.01, xanchor="left", font=dict(size=22, color=INK)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    for ann in fig.layout.annotations:           # left-align the headline subtitles
        if ann.text.startswith("<b>"):
            ann.update(x=ann.x - 0.0, xanchor="center", font=dict(size=13, color=INK))
    return fig


def main():
    out = pathlib.Path(__file__).parent
    fig = build_figure()
    html = out / "eval_dashboard.html"
    fig.write_html(html, include_plotlyjs="cdn")
    print(f"wrote {html}")
    try:
        png = out / "eval_dashboard.png"
        fig.write_image(png, scale=2)            # needs kaleido
        print(f"wrote {png}")
    except Exception as e:                        # flag-and-continue (repo convention)
        print(f"(PNG export skipped: {type(e).__name__}: {e}) — install `kaleido` for static export")


if __name__ == "__main__":
    main()
