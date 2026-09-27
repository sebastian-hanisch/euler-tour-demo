"""Plotly-Figuren: Karten (Tour-Wiedergabe, Gradhistogramm, gerichteter Fall mit Pfeilen) und Aufwands-/Anteilskurven. Alle Achsen fest (fixedrange); Karten mit gleichem Maßstab nutzen `scaleanchor`
mit autorange und zwei unsichtbaren Eckpunkten."""

import math

import plotly.graph_objects as go

TEAL, ORANGE, BLUE, RED, GREY, LIGHT = "#2F6B65", "#f58518", "#4c78a8", "#e45756", "#b7bec7", "#e8ebee"


def _base_layout(fig, height=430, title=None):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=36 if title else 10, b=10), showlegend=False, title=dict(text=title, x=0.01, font=dict(size=14)) if title else None,
                       plot_bgcolor="white")
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig


def _corners(fig, xy):
    pad = 0.4
    fig.add_trace(go.Scatter(x=[xy[:, 0].min() - pad, xy[:, 0].max() + pad], y=[xy[:, 1].min() - pad, xy[:, 1].max() + pad], mode="markers", marker=dict(opacity=0), hoverinfo="skip"))


def _name(inst, v):
    return inst.labels[v] if inst.labels else str(v)


def _lines(xy, pairs, color, width):
    xs, ys = [], []
    for u, v in pairs:
        x0, y0 = xy[u]
        x1, y1 = xy[v]
        xs += [x0, x1, None]
        ys += [y0, y1, None]
    return go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width), hoverinfo="skip")


def _arrowheads(xy, pairs, at=0.62):
    px, py, angles = [], [], []
    for u, v in pairs:
        x0, y0 = xy[u]
        x1, y1 = xy[v]
        px.append(x0 + (x1 - x0) * at)
        py.append(y0 + (y1 - y0) * at)
        angles.append(math.degrees(math.atan2(x1 - x0, y1 - y0)) % 360)
    return px, py, angles


def _add_arrows(fig, xy, pairs, color=GREY, size=7):
    if not pairs:
        return
    px, py, angles = _arrowheads(xy, pairs)
    fig.add_trace(go.Scatter(x=px, y=py, mode="markers", marker=dict(symbol="triangle-up", size=size, color=color, angle=angles), hoverinfo="skip", showlegend=False))


def build_network(inst, height=380):
    """Der bloße Graph, ohne Tour - Übersicht auf der ersten Karte."""
    fig = go.Figure()
    xy = inst.xy
    fig.add_trace(_lines(xy, inst.edges, GREY, 1.6))
    if inst.directed:
        _add_arrows(fig, xy, inst.edges)
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers+text" if inst.labels else "markers", text=[_name(inst, v) for v in range(inst.n)] if inst.labels else None,
                              textposition="top center", marker=dict(size=13 if inst.labels else 7, color=TEAL, line=dict(color="white", width=1))))
    _corners(fig, xy)
    return _base_layout(fig, height)


def build_replay_map(inst, tour, k, bridge_flags=None, height=430):
    """Zustand nach den ersten `k` Tour-Schritten: bereits benutzte Kanten teal, die aktuelle Kante orange (rot, wenn sie laut `bridge_flags` eine Brücke war), unbenutzte Kanten grau dünn."""
    xy = inst.xy
    used_pairs = [(tour[i], tour[i + 1]) for i in range(k)]
    used_set = {tuple(sorted(p)) for p in used_pairs} if not inst.directed else set(used_pairs)
    remaining = [(u, v) for u, v in inst.edges if (tuple(sorted((u, v))) if not inst.directed else (u, v)) not in used_set]
    fig = go.Figure()
    fig.add_trace(_lines(xy, remaining, GREY, 1.4))
    if inst.directed:
        _add_arrows(fig, xy, remaining, GREY, 6)
    if k > 1:
        fig.add_trace(_lines(xy, used_pairs[:-1], TEAL, 3))
        if inst.directed:
            _add_arrows(fig, xy, used_pairs[:-1], TEAL, 8)
    if k >= 1:
        current = used_pairs[-1]
        is_bridge = bool(bridge_flags and bridge_flags[k - 1])
        fig.add_trace(_lines(xy, [current], RED if is_bridge else ORANGE, 4))
        if inst.directed:
            _add_arrows(fig, xy, [current], RED if is_bridge else ORANGE, 10)
    visited = set(tour[: k + 1])
    colors = [ORANGE if v == tour[k] else (TEAL if v in visited else LIGHT) for v in range(inst.n)]
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers+text" if inst.labels else "markers", text=[_name(inst, v) for v in range(inst.n)] if inst.labels else None,
                              textposition="top center", marker=dict(size=13 if inst.labels else 7, color=colors, line=dict(color="white", width=1))))
    _corners(fig, xy)
    return _base_layout(fig, height)


def build_degree_hist(inst, degrees, odd_nodes):
    odd_set = set(odd_nodes)
    labels = [_name(inst, v) for v in range(inst.n)]
    colors = [RED if v in odd_set else TEAL for v in range(inst.n)]
    fig = go.Figure(go.Bar(x=labels, y=degrees, marker_color=colors))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, plot_bgcolor="white", bargap=0.25)
    fig.update_xaxes(fixedrange=True, title="Knoten" if inst.n <= 30 else None, showticklabels=inst.n <= 30,
                      **(dict(tickmode="array", tickvals=labels, ticktext=labels) if inst.n <= 30 else {}))
    fig.update_yaxes(fixedrange=True, title="Grad", gridcolor=LIGHT)
    return fig


def build_cost_sweep(rows):
    ns = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[r["hierholzer"] for r in rows], mode="lines+markers", name="Hierholzer", line=dict(color=TEAL, width=2)))
    fig.add_trace(go.Scatter(x=ns, y=[r["fleury"] for r in rows], mode="lines+markers", name="Fleury", line=dict(color=ORANGE, width=2)))
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(x=0.02, y=0.98), plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True, title="Knotenzahl n", gridcolor=LIGHT)
    fig.update_yaxes(fixedrange=True, title="Elementarschritte", type="log", gridcolor=LIGHT)
    return fig


def build_share_sweep(rows, title=""):
    sides = [r["side"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sides, y=[r["share_circuit"] for r in rows], name="Eulerkreis", marker_color=TEAL))
    fig.add_trace(go.Bar(x=sides, y=[r["share_path"] for r in rows], name="Eulerweg", marker_color=BLUE))
    fig.add_trace(go.Bar(x=sides, y=[r["share_none"] for r in rows], name="keins", marker_color=GREY))
    fig.update_layout(barmode="stack", height=340, margin=dict(l=10, r=10, t=24 if title else 10, b=60), showlegend=True, legend=dict(x=0.02, y=-0.22, orientation="h"), plot_bgcolor="white",
                       title=dict(text=title, x=0.01, font=dict(size=13)) if title else None)
    fig.update_xaxes(fixedrange=True, title="Seitenlänge", gridcolor=LIGHT)
    fig.update_yaxes(fixedrange=True, title="Anteil", range=[0, 1], gridcolor=LIGHT)
    return fig
