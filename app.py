"""Eulertouren: Hierholzer gegen Fleury - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Viertes Stück der Graphen-und-Netzwerke-Reihe der "Konzepte"-Reihe. Kind der Brücken-Demo: Fleury braucht den Brückentest bei jedem Schritt, Hierholzer kommt ohne ihn aus.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import eul_algorithm as ea
import eul_constants as C
import eul_evaluation as ev
import eul_scenario as es
from eul_evaluation import Settings, analyse
from eul_presets import apply_preset, bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, store_from_widget, sync_query_params
from eul_visualization import build_cost_sweep, build_degree_hist, build_network, build_replay_map, build_share_sweep

st.set_page_config(page_title="Eulertouren – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _directed_analysis(n, n_cycles, target, seed):
    inst = es.euler_instance(n, n_cycles, True, target, seed)
    adj = ea.adjacency_directed(inst.n, inst.edges)
    cls = ea.classify_directed(adj)
    hr = ea.hierholzer_directed(adj) if cls == "circuit" else None
    return inst, adj, cls, hr


@st.cache_data(show_spinner=False)
def _cost_sweep():
    return ev.cost_sweep(C.COST_NS)


@st.cache_data(show_spinner=False)
def _share_sweep(nettype):
    return ev.eulerian_share_sweep(nettype, C.SHARE_SIDES, seeds=C.SHARE_SEEDS)


def _german(x):
    return f"{x:,}".replace(",", ".")


st.title("🖊️ Eulertouren – jede Kante genau einmal")
st.markdown(
    """
**Viertes Stück der Graphen-und-Netzwerke-Reihe.** Ein **Eulerkreis** besucht jede Kante eines Netzes genau einmal und kehrt zum Start zurück; ein **Eulerweg** tut dasselbe, ohne zurückzukehren. Ein
zusammenhängendes Netz hat genau dann einen Eulerkreis, wenn **jeder Knoten geraden Grad hat**, und genau dann einen Eulerweg, wenn **genau zwei Knoten ungeraden Grad haben** - die Zahl der ungeraden
Knoten ist nach dem Handschlaglemma immer gerade.

Zwei Verfahren finden dieselbe Tour: **Hierholzer** (Teilkreise verschmelzen, O(n + m)) und **Fleury** (schrittweise, meidet eine **Brücke** im noch nicht benutzten Restnetz, außer es bleibt keine
Alternative - dafür braucht er bei *jedem* Schritt den Brückentest aus der Brücken-Demo, O(m·(n + m))). Gemessen wird der Aufwandsunterschied und wie selten ein Zufallsnetz überhaupt spontan eulersch ist.
"""
)
st.caption(
    "Kind der Brücken-Demo (viertes Stück der Graphen-und-Netzwerke-Reihe); die übrigen Stücke der Reihe (Graphfärbung, Zentralität, Strukturkennzahlen, Robustheit, Kaskaden, kritische Knoten härten, Bandbreite, Bandbreite von G(n,k,b)) sind inzwischen gebaut. "
    "Die Arc-Routing-Demo (Chinesischer Postbote) paart ungerade Knoten, um ein Netz erst eulersch zu MACHEN - hier wird vorausgesetzt, dass es (fast) schon eins ist, und die Tour selbst gesucht."
)

with st.expander("So funktionieren Hierholzer und Fleury", expanded=True):
    st.markdown(
        """
1. **Hierholzer:** vom Start aus einem unbenutzten Nachbarn folgen, bis keiner mehr da ist; dann rückwärts über den entstandenen Pfad an der Stelle einen Teilkreis einfügen, an der ein Knoten noch
   unbenutzte Kanten hat. Jede Kante wird genau einmal angesehen: O(n + m), unabhängig davon, wie die Tour verläuft.
2. **Fleury:** vom aktuellen Knoten aus wird eine Kante gewählt, die im *Restnetz* KEINE Brücke ist - eine Brücke würde das restliche Netz in zwei Teile trennen, von denen einer dann nie mehr erreichbar
   wäre. Nur wenn jede verbleibende Kante eine Brücke ist, wird sie überquert. Der Brückentest (Tarjans Low-Link, wie in der Brücken-Demo) läuft dafür bei *jedem* Schritt neu über das ganze Restnetz.
3. **Existenz:** ein Eulerkreis existiert genau dann, wenn das ganze Netz zusammenhängend ist (auch ein einzelner Knoten ohne Kante zählt mit) und jeder Knoten geraden Grad hat; ein Eulerweg, wenn
   zusätzlich genau zwei Knoten ungeraden Grad haben - dann muss die Tour an einem beginnen und am anderen enden.
        """
    )

if C.PRESETS:
    st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
    preset_names = list(C.PRESETS.keys())
    for row in (preset_names[:4], preset_names[4:]):
        if not row:
            continue
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()
ss = st.session_state

with st.sidebar:
    st.header("⚙️ Einstellungen")
    kind = st.radio("Instanz", options=list(C.KINDS), format_func=lambda v: C.KIND_LABELS[v], key="kind_select",
                     help="Eulernetz: konstruiert aus zufälligen, kantendisjunkten Kreisen, immer eulersch (oder mit genau 2 ungeraden Knoten). Betriebsnetz/Zufallsgraph: gewöhnliche Netze wie in "
                     "Stück 1-3, typischerweise NICHT eulersch. Haus vom Nikolaus: das klassische Kinderrätsel.")
    n, n_cycles, target, side, nettype = C.DEFAULT_N, C.DEFAULT_CYCLES, "circuit", C.DEFAULT_SIDE, "grid"
    if kind == "euler":
        n = st.slider("Knotenzahl", *bounds("n_slider"), value=int(ss["n_slider"]), key="n_widget", on_change=store_from_widget, args=("n_slider",))
        n_cycles = st.slider("Zahl der Kreise", *bounds("cycles_slider"), value=int(ss["cycles_slider"]), key="cycles_widget", on_change=store_from_widget, args=("cycles_slider",),
                              help="Ein Basiskreis über alle Knoten plus weitere, kantendisjunkte Kreise über zufälligen Teilmengen.")
        target = st.radio("Ziel", options=list(C.TARGETS), format_func=lambda v: C.TARGET_LABELS[v], key="target_select",
                           help="Eulerkreis: alle Grade gerade. Eulerweg: eine Kante wird entfernt, genau zwei Knoten werden ungerade.")
        seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), value=int(ss["seed_input"]), key="seed_widget", step=1, on_change=store_from_widget, args=("seed_input",))
        st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    elif kind == "city":
        side = st.slider("Kreuzungen je Seite", *bounds("side_slider"), value=int(ss["side_slider"]), key="side_widget", on_change=store_from_widget, args=("side_slider",))
        nettype = st.radio("Netztyp", options=list(C.NETTYPES), format_func=lambda v: C.NETTYPE_LABELS[v], index=list(C.NETTYPES).index(ss["nettype_select"]), key="nettype_widget",
                            on_change=store_from_widget, args=("nettype_select",))
        seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), value=int(ss["seed_input"]), key="seed_widget", step=1, on_change=store_from_widget, args=("seed_input",))
        st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    else:
        seed = 0
    order = st.radio("Nachbarreihenfolge", options=list(C.ORDERS), format_func=lambda v: C.ORDER_LABELS[v], key="order_select",
                      help="Ändert die Wiedergabe (welche der möglichen Touren gefunden wird), nie, OB eine Tour existiert.")

sync_query_params({"kind_select": kind, "n_slider": int(n) if kind == "euler" else int(ss["n_slider"]), "cycles_slider": int(n_cycles) if kind == "euler" else int(ss["cycles_slider"]),
                    "target_select": target if kind == "euler" else ss["target_select"], "side_slider": int(side) if kind == "city" else int(ss["side_slider"]),
                    "nettype_select": nettype if kind == "city" else ss["nettype_select"], "order_select": order, "seed_input": int(seed) if kind != "textbook" else int(ss["seed_input"]),
                    "eul_step": int(ss["eul_step"])})

settings = Settings(kind, int(n) if kind == "euler" else C.DEFAULT_N, int(n_cycles) if kind == "euler" else C.DEFAULT_CYCLES, target if kind == "euler" else "circuit", False,
                     nettype if kind == "city" else "grid", int(side) if kind == "city" else C.DEFAULT_SIDE, int(seed) if kind != "textbook" else 0, order)
with st.spinner("Rechne..."):
    a = _analysis(settings)
inst = es.textbook_instance() if kind == "textbook" else (es.euler_instance(settings.n, settings.n_cycles, False, settings.target, settings.seed) if kind == "euler"
                                                            else es.city_instance(settings.side, settings.nettype, settings.seed))
adj = ea.adjacency(inst.n, inst.edges, order, settings.seed)
names = (lambda v: inst.labels[v]) if inst.labels else (lambda v: str(v))

st.markdown("## 🎯 Das Netz und seine Tour")
kind_label = {"euler": "Eulernetz", "city": C.NETTYPE_LABELS[nettype] if kind == "city" else "", "textbook": "Haus vom Nikolaus"}[kind]
cls_label = {"circuit": "Eulerkreis", "path": "Eulerweg", "none": "weder Kreis noch Weg"}[a.classification]
st.markdown(f"**{a.n} Knoten, {_german(a.m)} Kanten** ({kind_label}), **{a.odd_count} ungerade Knoten** → **{cls_label}**.")
step = st.select_slider("Schritt", options=list(C.STEPS), key="eul_step", format_func=lambda s: C.STEPS[s])

if step == 1:
    if a.classification == "none":
        st.info(f"Für diese Einstellung existiert keine Eulertour ({a.odd_count} ungerade Knoten bzw. das Netz ist nicht zusammenhängend).")
    else:
        algo = st.radio("Verfahren", options=list(C.ALGOS), format_func=lambda v: C.ALGO_LABELS[v], horizontal=True, key="algo_select")
        result = a.hierholzer if algo == "hierholzer" else a.fleury
        n_steps = len(result.tour) - 1
        ss["tour_k"] = n_steps if "tour_k" not in ss else min(max(1, int(ss["tour_k"])), n_steps)
        k = st.slider("Tour-Schritt", 1, n_steps, key="tour_k", help="Wie viele Kanten der Tour sind schon benutzt.")
        bridge_flags = None
        if algo == "fleury":
            bridge_flags = [None] + [e[4] for e in result.events]
        st.plotly_chart(build_replay_map(inst, result.tour, k, bridge_flags), width="stretch", key=f"s1_map_{algo}_{k}")
        v_from, v_to = result.tour[k - 1], result.tour[k]
        msg = f"**Schritt {k} von {n_steps}:** {names(v_from)} → {names(v_to)}."
        if algo == "fleury":
            crossed = bridge_flags[k]
            msg += " Diese Kante ist eine **Brücke** im Restnetz, aber die einzig noch mögliche." if crossed else " Es gab eine Alternative ohne Brücke."
        st.markdown(msg)
        st.caption(f"Hierholzer braucht {_german(a.hierholzer.steps)} Elementarschritte, Fleury {_german(a.fleury.steps)} ({a.fleury.bridge_calls} Brückentests) - "
                   f"das {a.ratio:.1f}-Fache." if a.ratio else "")
elif step == 2:
    c1, c2, c3 = st.columns(3)
    c1.metric("Ungerade Knoten", a.odd_count, delta_color="off")
    c2.metric("Zusammenhängend", "ja" if ea.is_connected(adj) else "nein", delta_color="off")
    c3.metric("Klassifikation", cls_label, delta_color="off")
    cc1, cc2 = st.columns([3, 2])
    with cc1:
        st.plotly_chart(build_network(inst), width="stretch", key="s2_map")
        st.caption("Das Netz ohne Tour.")
    with cc2:
        st.plotly_chart(build_degree_hist(inst, ea.degrees(adj), ea.odd_nodes(adj)), width="stretch", key="s2_hist")
        st.caption("Grad je Knoten; ungerade Knoten rot.")
elif step == 3:
    st.markdown("Dieselbe Konstruktion (Basiskreis + zusätzliche Kreise), aber mit **gerichteten** Bögen: jeder Kreis erhöht Eingangs- UND Ausgangsgrad seiner Knoten um je 1.")
    n3, c3_, t3, seed3 = (int(n), int(n_cycles), target, int(seed)) if kind == "euler" else (C.DEFAULT_N, C.DEFAULT_CYCLES, "circuit", int(ss["seed_input"]))
    dinst, dadj, dcls, dhr = _directed_analysis(n3, c3_, t3, seed3)
    in_deg = [0] * dinst.n
    out_deg = [len(lst) for lst in dadj]
    for lst in dadj:
        for v in lst:
            in_deg[v] += 1
    balanced = out_deg == in_deg
    e1, e2, e3 = st.columns(3)
    e1.metric("Balanciert (Ein=Aus)", "ja" if balanced else "nein", delta_color="off")
    e2.metric("Zusammenhängend", "ja" if ea.directed_is_connected(dadj) else "nein", delta_color="off")
    e3.metric("Eulerkreis", "ja" if dcls == "circuit" else "nein", delta_color="off")
    st.plotly_chart(build_network(dinst), width="stretch", key="s3_map")
    if dhr:
        st.caption(f"Hierholzer (gerichtet) findet eine Tour über alle {dinst.m} Bögen mit {_german(dhr.steps)} Elementarschritten.")
    else:
        st.caption("Für diese Einstellung ist der gerichtete Graph nicht eulersch.")
else:
    st.markdown("#### 🔬 Aufwand: Hierholzer gegen Fleury")
    if st.button("Über die Größe messen (kann einen Moment dauern)", key="cost_start"):
        ss["cost_done"] = True
    if ss.get("cost_done"):
        with st.spinner("Rechne..."):
            rows_cost = _cost_sweep()
        st.plotly_chart(build_cost_sweep(rows_cost), width="stretch", key="s4_cost")
        st.caption(f"Median über 5 feste Instanzen je Größe (Eulernetz, Eulerkreis). Bei n = {rows_cost[-1]['n']} braucht Fleury das {rows_cost[-1]['ratio']:.0f}-Fache von Hierholzers Schritten.")
    st.markdown("#### 🔬 Wie oft ist ein Zufallsnetz spontan eulersch?")
    if st.button("Über die Größe messen", key="share_start"):
        ss["share_done"] = True
    if ss.get("share_done"):
        with st.spinner("Rechne..."):
            rows_grid = _share_sweep("grid")
            rows_random = _share_sweep("random")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.plotly_chart(build_share_sweep(rows_grid, C.NETTYPE_LABELS["grid"]), width="stretch", key="s4_share_grid")
        with sc2:
            st.plotly_chart(build_share_sweep(rows_random, C.NETTYPE_LABELS["random"]), width="stretch", key="s4_share_random")
        st.caption(f"Anteil über {len(C.SHARE_SEEDS)} feste Instanzen je Größe. Ohne Konstruktion ist Eulerizität selten: schon ab {C.SHARE_SIDES[2]} × {C.SHARE_SIDES[2]} Knoten praktisch nie mehr.")

st.markdown("---")

st.markdown("## 🎯 Was das Netz verrät")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Ungerade Knoten", a.odd_count, delta_color="off")
r2.metric("Klassifikation", cls_label, delta_color="off")
r3.metric("Aufwand Hierholzer", _german(a.hierholzer.steps) if a.hierholzer else "-", delta_color="off")
r4.metric("Aufwand Fleury", _german(a.fleury.steps) if a.fleury else "-", delta_color="off")

st.markdown("---")

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Zufallsnetze sind meistens eulersch** | Ohne gezielte Konstruktion praktisch nie: schon ein Raster ab 3 × 3 Knoten hat an jedem Rand Knoten ungeraden Grades. | - |
| **Fleury ist nur wenig teurer als Hierholzer** | Der Faktor wächst mit der Größe (O(m) gegen O(m·(n+m))) - bei größeren Netzen wird der Unterschied deutlich. | - |
| **Isolierte Knoten sind harmlos** | Ein einzelner Knoten ohne Kante macht das ganze Netz nicht eulersch (networkx-Konvention, hier bestätigt statt angenommen). | - |
| **Fleury funktioniert auch gerichtet** | Hier nur für ungerichtete Netze gebaut; der gerichtete Fall nutzt nur Hierholzer. | - |
| **Elementarschritte zeigen den Aufwand** | Sie zählen Knoten- und Kantenbesuche, keine Rechenzeit. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Graph.** $G=(V,E)$, $n=|V|$, $m=|E|$. Ein **Eulerkreis** ist ein geschlossener Kantenzug, der jede Kante genau einmal nutzt; ein **Eulerweg** dasselbe ohne Rückkehr zum Start.

**Satz (Euler 1736, Hierholzer 1873).** Ein zusammenhängendes $G$ hat einen Eulerkreis genau dann, wenn jeder Knoten geraden Grad hat; einen Eulerweg genau dann, wenn genau 0 oder 2 Knoten ungeraden
Grad haben (im Fall von 2 muss die Tour an einem beginnen und am anderen enden). Die Zahl der ungeraden Knoten ist stets gerade ($\sum_v \deg(v) = 2m$, Handschlaglemma).

**Hierholzer.** Iterativ einem unbenutzten Nachbarn folgen, bis keiner mehr da ist; die entstandene Sackgasse rückwärts abgehen und an jedem Knoten mit noch unbenutzten Kanten einen dort neu gefundenen
Teilkreis einfügen. Jede Kante wird konstant oft angesehen: $O(n+m)$.

**Fleury.** Von $u$ aus wird eine Kante $(u,v)$ gewählt, die im Restgraphen $G'$ (nur unbenutzte Kanten) **keine Brücke** ist, sofern eine solche existiert; ist $(u,v)$ die letzte verbleibende Kante,
wird sie überquert. Der Brückentest (Tarjans Low-Link, $O(n+m)$) läuft bei jedem der $m$ Schritte neu: $O(m(n+m))$ insgesamt.

**Gerichteter Fall.** Ein gerichteter Graph hat einen Eulerkreis genau dann, wenn Eingangsgrad gleich Ausgangsgrad an jedem Knoten ist und der zugrunde liegende (ungerichtete) Graph zusammenhängend ist.

**Literatur.** Euler, L. (1741). *Solutio problematis ad geometriam situs pertinentis.* Commentarii Academiae Scientiarum Imperialis Petropolitanae 8, 128–140. Hierholzer, C., & Wiener, C. (1873).
*Ueber die Möglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren.* Mathematische Annalen 6(1), 30–32 (posthum). Fleury, M. (1883). *Deux problèmes de géométrie de situation.*
Journal de mathématiques élémentaires, 2e série, 2, 257–261.

Implementiert in `eul_algorithm.py` (Hierholzer, Fleury, Low-Link-Kopie, Klassifikation), `eul_scenario.py` (Instanzen), `eul_evaluation.py` (Kennzahlen, Sweeps).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html)."
)
