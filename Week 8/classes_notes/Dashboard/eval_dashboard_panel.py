"""
eval_dashboard_panel.py — the same Week 7 · Day 5 evaluation dashboard as an
INTERACTIVE app, built with HoloViz **Panel** + **Plotly**.

This is the "interactive filters for drill-down" deliverable from the lab — the
code equivalent of a Tableau/PowerBI dashboard. Pick categories in the sidebar
and every panel + KPI recomputes.

Run it LIVE (recommended):
    panel serve eval_dashboard_panel.py --show

Quick static snapshot (no live callbacks, just to eyeball it):
    python eval_dashboard_panel.py

Design echoes the lesson: KPI cards (Layer-3 metrics), one-chart-one-message
panels, headline titles, color-the-signal / gray-the-noise, reference lines,
the right chart per question. Single-axis figures here, so add_vline/add_hline
are used directly (the multi-panel Plotly file needs the add_shape workaround).
"""
from __future__ import annotations
import pathlib
import panel as pn
import plotly.graph_objects as go

import eval_data as ed

pn.extension("plotly", sizing_mode="stretch_width")

INK = "#1e1e1e"; MUTE = "#868e96"; SIGNAL = "#e03131"; GOOD = "#2f9e44"; BLUE = "#1971c2"
TARGET = 7.0
FULL = ed.load_eval()
ALL_CATS = sorted(FULL["category"].unique())

_BASE = dict(template="plotly_white", height=320,
             margin=dict(l=70, r=30, t=64, b=40), showlegend=False,
             font=dict(color=INK))


def fig_bar(df):
    cat = ed.by_category(df)
    worst = cat.iloc[0]["category"]
    colors = [SIGNAL if c == worst else MUTE for c in cat["category"]]
    n_below = int((cat["avg_score"] < TARGET).sum())
    phrase = "the only category" if n_below == 1 else f"worst of {n_below}"
    fig = go.Figure(go.Bar(
        y=cat["category"], x=cat["avg_score"], orientation="h", marker_color=colors,
        text=[f"{v:.1f}" for v in cat["avg_score"]], textposition="outside",
        cliponaxis=False, hoverinfo="skip"))
    fig.add_vline(x=TARGET, line=dict(color=INK, dash="dash", width=2),
                  annotation_text=f"target {TARGET:.0f}", annotation_position="bottom right")
    fig.update_layout(title=f"<b>{worst.replace('_',' ').title()} is the weak spot</b> — "
                      f"{cat.iloc[0]['avg_score']:.1f}/10, {phrase} below target",
                      xaxis_range=[0, 10], **_BASE)
    return fig


def fig_trend(df):
    wk = ed.weekly_trend(df)
    fig = go.Figure(go.Scatter(x=wk["week"], y=wk["avg_score"], mode="lines+markers",
                               line=dict(color=BLUE, width=3), marker=dict(size=6),
                               hoverinfo="skip"))
    fig.add_hline(y=TARGET, line=dict(color=MUTE, dash="dot", width=1.5))
    # add_shape + add_annotation instead of add_vline: on a date axis add_vline's
    # auto-placed annotation tries to average the x string and crashes.
    drift_x = ed.DRIFT_WEEK.strftime("%Y-%m-%d")
    fig.add_shape(type="line", xref="x", yref="y domain", x0=drift_x, x1=drift_x,
                  y0=0, y1=1, line=dict(color=SIGNAL, dash="dash", width=2))
    fig.add_annotation(xref="x", yref="y domain", x=drift_x, y=0.96,
                       text="prompt edited", showarrow=False, yanchor="top",
                       xanchor="left", font=dict(size=11, color=SIGNAL),
                       bgcolor="rgba(255,255,255,0.7)")
    fig.update_layout(title="<b>Scores step down after the Oct 1 prompt edit</b> — judge drift",
                      yaxis_range=[0, 10], **_BASE)
    return fig


def fig_hist(df):
    fig = go.Figure(go.Histogram(x=df["judge_score"], nbinsx=20, marker_color=BLUE,
                                 marker_line_color="white", marker_line_width=0.5,
                                 hoverinfo="skip"))
    fig.add_vline(x=TARGET, line=dict(color=INK, dash="dash", width=2))
    fig.update_layout(title="<b>A persistent low-score tail</b> — the billing cluster",
                      xaxis_title="judge score", xaxis_range=[0, 10], **_BASE)
    return fig


def fig_accuracy(df):
    cat = ed.by_category(df).sort_values("accuracy")
    worst = ed.by_category(df).iloc[0]["category"]
    colors = [SIGNAL if c == worst else GOOD for c in cat["category"]]
    fig = go.Figure(go.Bar(y=cat["category"], x=cat["accuracy"], orientation="h",
                           marker_color=colors, text=[f"{v:.0f}%" for v in cat["accuracy"]],
                           textposition="outside", cliponaxis=False, hoverinfo="skip"))
    fig.add_vline(x=80, line=dict(color=INK, dash="dash", width=2),
                  annotation_text="80%", annotation_position="bottom right")
    fig.update_layout(title="<b>Accuracy tracks the judge score</b> — billing weakest on both",
                      xaxis_title="accuracy %", xaxis_range=[0, 100], **_BASE)
    return fig


def _num(name, value, fmt, color):
    return pn.indicators.Number(name=name, value=value, format=fmt,
                                font_size="34pt", title_size="12pt",
                                default_color=color)


def build_app():
    cat_filter = pn.widgets.CheckButtonGroup(
        name="Category", value=ALL_CATS, options=ALL_CATS, button_type="primary")

    @pn.depends(cat_filter)
    def kpi_row(cats):
        d = FULL[FULL["category"].isin(cats)] if cats else FULL
        k = ed.kpis(d)
        return pn.FlexBox(
            _num("Avg judge score /10", k["avg_score"], "{value:.2f}",
                 GOOD if k["avg_score"] >= TARGET else SIGNAL),
            _num("Category accuracy", k["accuracy"], "{value:.1f}%",
                 GOOD if k["accuracy"] >= 80 else SIGNAL),
            _num("Avg cost / ticket", k["cost_per_run"], "${value:.4f}", BLUE),
            _num("P95 latency", k["p95_latency"], "{value:.2f} s",
                 GOOD if k["p95_latency"] <= 2.5 else SIGNAL),
            _num("Tickets scored", k["n"], "{value:.0f}", INK),
            justify_content="space-between")

    @pn.depends(cat_filter)
    def panels(cats):
        d = FULL[FULL["category"].isin(cats)] if cats else FULL
        cfg = {"displayModeBar": False}
        grid = pn.GridBox(ncols=2, sizing_mode="stretch_width")
        for f in (fig_bar(d), fig_trend(d), fig_hist(d), fig_accuracy(d)):
            grid.append(pn.pane.Plotly(f, config=cfg, sizing_mode="stretch_width"))
        return grid

    meta = ("**{model}** · {prompt} · judge {judge}  \n"
            "*So what:* fix **billing** first — it fails accuracy AND score.").format(**ed.RUN_META)

    return pn.template.FastListTemplate(
        title="Support-Ticket Scoring — Evaluation Dashboard",
        sidebar=[pn.pane.Markdown("### Filter"), cat_filter,
                 pn.pane.Markdown("---"), pn.pane.Markdown(meta)],
        main=[kpi_row, panels],
        accent_base_color=BLUE, header_background=BLUE,
    )


app = build_app()
app.servable()


if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "panel_dashboard.html"
    app.save(out)   # static snapshot (live filtering needs `panel serve`)
    print(f"saved {out} (static snapshot)")
    print("LIVE interactive app:")
    print(f"  panel serve {pathlib.Path(__file__).name} --show")
