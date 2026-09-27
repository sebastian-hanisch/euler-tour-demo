"""Regler-Grenzen, feste Annahmen, gemessene Werte und Presets."""

SPACING = 1.0
JITTER = 0.18
SIDE_MIN, SIDE_MAX, DEFAULT_SIDE = 4, 20, 8
SEED_MAX = 999999
DEFAULT_SEED = 35

N_MIN, N_MAX, DEFAULT_N = 6, 60, 16
CYCLES_MIN, CYCLES_MAX, DEFAULT_CYCLES = 1, 10, 3

KINDS = ("euler", "city", "textbook")
KIND_LABELS = {"euler": "Eulernetz (konstruiert)", "city": "Betriebsnetz / Zufallsgraph", "textbook": "Lehrbuchbeispiel: Haus vom Nikolaus (5 Knoten)"}
NETTYPES = ("grid", "random")
NETTYPE_LABELS = {"grid": "Raster (Straßennetz)", "random": "Zufallsgraph (gleiche Kantenzahl)"}
TARGETS = ("circuit", "path")
TARGET_LABELS = {"circuit": "Eulerkreis (alle Grade gerade)", "path": "Eulerweg (genau 2 ungerade Knoten)"}
ORDERS = ("fixed", "shuffled")
ORDER_LABELS = {"fixed": "feste Reihenfolge (nach Knotennummer)", "shuffled": "gemischt (nach Seed)"}
ALGOS = ("hierholzer", "fleury")
ALGO_LABELS = {"hierholzer": "Hierholzer (Kreise verschmelzen)", "fleury": "Fleury (Brückentest je Schritt)"}
STEPS = {1: "1 · Hierholzer und Fleury in Aktion", 2: "2 · Eulerkreis oder -weg?", 3: "3 · Gerichteter Fall", 4: "4 · Aufwand und Zufalls-Sweep"}

SWEEP_SEEDS = tuple(range(100000, 100005))
COST_NS = (8, 12, 16, 20, 30, 40, 60)
SHARE_SIDES = (2, 3, 4, 5, 6, 8)
SHARE_SEEDS = tuple(range(100000, 100100))

# --- Gemessene Werte (2026-09-27, alle Werte über ev.* nachgerechnet, s. tests/test_claims.py) ---
# AUFWAND (Eulerkreis-Netze, Median über 5 feste Instanzen Seeds 100000-100004): Hierholzer/Fleury-Elementarschritte 55/378 (n=8), 88/927 (n=12), 112/1441 (n=16), 154/2821 (n=20), 187/3728 (n=30),
#   268/7989 (n=40), 325/9830 (n=60) - der Faktor wächst von 6.9 auf 30.2.
# ANTEIL EULERSCH (Betriebsnetz/Zufallsgraph, 100 feste Instanzen je Größe): bei Seitenlänge 2 (4 Knoten) ist das Raster IMMER ein Eulerkreis (ein einfacher 4-Kreis), der Zufallsgraph zu 35 % Kreis
#   und 65 % Weg (also 100 % eulersch); ab Seitenlänge 4 (16 Knoten) ist praktisch KEINE Instanz mehr eulersch (0 % bei beiden Netztypen) - ohne gezielte Konstruktion ist Eulerizität selten.

PRESETS = {
    "Haus vom Nikolaus (Lehrbuch)": {"kind": "textbook", "step": 1},
    "Eulerkreis (Standardfall)": {"kind": "euler", "n": 16, "n_cycles": 3, "target": "circuit", "seed": 35, "order": "fixed", "step": 2},
    "Eulerweg (ein ungerades Paar)": {"kind": "euler", "n": 16, "n_cycles": 3, "target": "path", "seed": 35, "order": "fixed", "step": 2},
    "Gerichteter Eulerkreis": {"kind": "euler", "n": 16, "n_cycles": 3, "target": "circuit", "seed": 35, "order": "fixed", "step": 3},
    "Betriebsnetz (nicht eulersch)": {"kind": "city", "side": 8, "nettype": "grid", "seed": 35, "order": "fixed", "step": 2},
    "Zufallsgraph (viele ungerade Knoten)": {"kind": "city", "side": 8, "nettype": "random", "seed": 35, "order": "fixed", "step": 2},
    "Aufwand: Hierholzer gegen Fleury": {"kind": "euler", "n": 60, "n_cycles": 5, "target": "circuit", "seed": 35, "order": "fixed", "step": 4},
}
PRESET_HELP = {
    "Haus vom Nikolaus (Lehrbuch)": "5 Kreuzungen, 8 Straßen: die beiden unteren Ecken (1, 2) haben Grad 3, die übrigen gerade - ein Eulerweg, kein Eulerkreis. Die Tour muss an einer der beiden unteren "
                                    "Ecken beginnen und an der anderen enden (das Kinderrätsel \"ohne den Stift abzusetzen\").",
    "Eulerkreis (Standardfall)": "16 Knoten, 29 Kanten (Vereinigung dreier kantendisjunkter Kreise): alle Grade gerade, ein Eulerkreis. Hierholzer braucht 88 Elementarschritte, Fleury 807 - das 9-Fache.",
    "Eulerweg (ein ungerades Paar)": "Dieselbe Konstruktion, aber eine Kante fehlt (28 statt 29 Kanten): genau 2 ungerade Knoten, ein Eulerweg. Hierholzer 85, Fleury 718 Elementarschritte.",
    "Gerichteter Eulerkreis": "16 Knoten, 38 Bögen (gerichtete Kreisvereinigung): Eingangsgrad = Ausgangsgrad an jedem Knoten, der zugrunde liegende Graph zusammenhängend - ein gerichteter Eulerkreis. "
                              "Hierholzer (gerichtet) braucht 115 Elementarschritte.",
    "Betriebsnetz (nicht eulersch)": "8 × 8 Kreuzungen (64 Knoten, 112 Straßen): 24 Kreuzungen haben ungeraden Grad (jede Randkreuzung) - kein Eulerkreis, kein Eulerweg.",
    "Zufallsgraph (viele ungerade Knoten)": "Dieselbe Knoten- und Kantenzahl (64, 112), aber beliebige Paare: 36 ungerade Knoten - noch mehr als im Raster.",
    "Aufwand: Hierholzer gegen Fleury": "Über die Größe gemessen (Eulerkreis-Netze): bei n = 8 braucht Fleury das 6.9-Fache von Hierholzers Schritten, bei n = 60 das 30.2-Fache (325 gegen 9830 "
                                        "Elementarschritte).",
}

