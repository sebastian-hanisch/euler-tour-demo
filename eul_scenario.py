"""Die Instanzen dieser Demo: ein **Eulernetz** (Vereinigung zufälliger, kantendisjunkter Kreise - jeder Kreis erhöht den Grad seiner Knoten um genau 2, macht die Konstruktion also automatisch
eulersch), ein **Betriebsnetz** (gestörtes Raster wie in den Geschwister-Demos, ungerichtet, garantiert zusammenhängend, kein Sperranteil - hier ist Eulerizität die Messgröße, nicht der Zerfall), ein
**Zufallsgraph** derselben Kantenzahl und das Lehrbuchbeispiel **Haus vom Nikolaus** (5 Knoten, 8 Kanten, genau 2 ungerade Knoten - das klassische "in einem Zug zeichnen"-Rätsel).

Knoten sind von 0 bis n - 1 durchnummeriert; Kanten sind Paare (u, v) mit u < v (ungerichtet) bzw. Bögen (u, v) für den gerichteten Fall, jeweils sortiert."""

import random
from dataclasses import dataclass, field

import numpy as np

import eul_constants as C


@dataclass(frozen=True)
class Instance:
    xy: np.ndarray                  # (n, 2)
    edges: tuple                    # ((u, v), ...) sortiert; bei directed=True: (u, v) ist ein Bogen u -> v
    kind: str = "euler"
    directed: bool = False
    seed: int = 0
    labels: tuple = field(default=())   # Knotennamen (nur Lehrbuchbeispiel)

    @property
    def n(self):
        return len(self.xy)

    @property
    def m(self):
        return len(self.edges)


def make_rng(seed, salt):
    """Zufallsquelle mit fester, plattformunabhängiger Zahlenfolge (Python-`random`)."""
    return random.Random(int(seed) * 1_000_003 + int(salt))


# --- Eulernetz: Vereinigung kantendisjunkter Kreise ----------------------------------------------------------------------------------------------


def _random_cycle(nodes, rng):
    """Eine zufällige Reihenfolge der gegebenen Knoten als Kreis (jeder Knoten hat in diesem Kreis Grad 2 bzw. Ein-/Ausgangsgrad je 1)."""
    order = list(nodes)
    rng.shuffle(order)
    return [(order[i], order[(i + 1) % len(order)]) for i in range(len(order))]


def _canon(u, v, directed):
    return (u, v) if directed or u < v else (v, u)


def euler_union_instance(n, n_cycles, directed, target, seed, min_cycle_len=3, max_tries=200):
    """Vereint einen **Basiskreis über alle n Knoten** (garantiert Zusammenhang und keinen isolierten Knoten - beides verlangt networkx' `is_eulerian` für den ganzen Graphen, nicht nur für die
    Knoten mit Kanten) mit `n_cycles - 1` weiteren zufälligen, **kantendisjunkten** Kreisen über zufälligen Teilmengen (Länge zwischen `min_cycle_len` und n): jeder Kreis erhöht ungerichtet den Grad,
    gerichtet Eingangs- UND Ausgangsgrad seiner Knoten um je 1. Kantendisjunkt ist entscheidend - teilen sich zwei Kreise eine Kante, würde sie im einfachen Graphen nur einmal gezählt und die
    Gradparität bräche; ein Kreis, der eine schon vorhandene Kante träfe, wird verworfen und neu gezogen (bis zu `max_tries` Versuche je Kreis). Die Vereinigung kantendisjunkter Kreise ist deshalb immer
    eulersch (Kreis). `target == "path"`: am Ende wird eine zufällige Kante entfernt (ungerichtet) bzw. ein neuer, bisher nicht vorhandener Bogen zwischen zwei Knoten ergänzt (gerichtet), wodurch genau
    zwei Knoten ungeraden Grad erhalten (Eulerweg statt Eulerkreis). Gibt (xy, edges) zurück."""
    if target not in ("circuit", "path"):
        raise ValueError(f"unbekanntes Ziel {target}")
    n = int(n)
    if n < 3:
        raise ValueError("mindestens 3 Knoten")
    rng = make_rng(seed, 2201)
    xy = np.array([[np.cos(2 * np.pi * i / n), np.sin(2 * np.pi * i / n)] for i in range(n)], dtype=float)
    edge_set = {_canon(u, v, directed) for u, v in _random_cycle(range(n), rng)}     # Basiskreis: alle Knoten, garantiert zusammenhängend

    def try_add_cycle():
        k = rng.randint(min(min_cycle_len, n), n)
        nodes = rng.sample(range(n), k)
        cyc = [_canon(u, v, directed) for u, v in _random_cycle(nodes, rng)]
        if len(set(cyc)) != len(cyc) or any(e in edge_set for e in cyc):
            return False
        edge_set.update(cyc)
        return True

    for _ in range(int(n_cycles) - 1):
        for _ in range(max_tries):
            if try_add_cycle():
                break
    if target == "path":
        if directed:
            touched = sorted({u for e in edge_set for u in e})
            candidates = [(u, v) for u in touched for v in touched if u != v and (u, v) not in edge_set]
            if candidates:
                edge_set.add(candidates[rng.randrange(len(candidates))])
        else:
            e = sorted(edge_set)[rng.randrange(len(edge_set))]
            edge_set.discard(e)
    return xy, tuple(sorted(edge_set))


def euler_instance(n=C.DEFAULT_N, n_cycles=C.DEFAULT_CYCLES, directed=False, target="circuit", seed=C.DEFAULT_SEED):
    xy, edges = euler_union_instance(n, n_cycles, directed, target, seed)
    return Instance(xy, edges, "euler", bool(directed), int(seed))


# --- Betriebsnetz (Raster) und Zufallsgraph, ungerichtet, garantiert zusammenhängend --------------------------------------------------------------


def grid_edges(side):
    out = []
    for r in range(side):
        for c in range(side):
            v = r * side + c
            if c + 1 < side:
                out.append((v, v + 1))
            if r + 1 < side:
                out.append((v, v + side))
    return out


def _connected_random_graph(n, m, rng):
    """Ein zusammenhängender ungerichteter Graph mit `n` Knoten und `m` Kanten: zuerst ein zufälliger Spannbaum (n - 1 Kanten), dann zufällige zusätzliche Kanten bis `m` erreicht ist."""
    order = list(range(n))
    rng.shuffle(order)
    edges = {(order[i], order[i + 1]) if order[i] < order[i + 1] else (order[i + 1], order[i]) for i in range(n - 1)}
    m = max(m, n - 1)
    max_m = n * (n - 1) // 2
    m = min(m, max_m)
    while len(edges) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        e = (u, v) if u < v else (v, u)
        edges.add(e)
    return sorted(edges)


def city_instance(side=C.DEFAULT_SIDE, nettype="grid", seed=C.DEFAULT_SEED, jitter=C.JITTER):
    if nettype not in C.NETTYPES:
        raise ValueError(f"unbekannter Netztyp {nettype}")
    side = int(side)
    if side < 2:
        raise ValueError("Seitenlänge mindestens 2")
    n = side * side
    rng = make_rng(seed, 4711)
    xy = np.array([[c * C.SPACING + rng.uniform(-jitter, jitter) * C.SPACING, r * C.SPACING + rng.uniform(-jitter, jitter) * C.SPACING] for r in range(side) for c in range(side)], dtype=float)
    if nettype == "grid":
        edges = sorted(grid_edges(side))
    else:
        edges = _connected_random_graph(n, len(grid_edges(side)), make_rng(seed, 9173))
    return Instance(xy, tuple(edges), "city", False, int(seed))


# --- Handgebautes Lehrbuchbeispiel: Haus vom Nikolaus --------------------------------------------------------------------------------------------

TEXTBOOK_LABELS = ("1", "2", "3", "4", "5")


def textbook_instance():
    """Das **Haus vom Nikolaus**: 5 Knoten (Quadrat 1-2-3-4 im Uhrzeigersinn plus Dachspitze 5 über der Kante 4-3), 8 Kanten: Quadratseiten 1-2, 2-3, 3-4, 4-1, beide Diagonalen 1-3 und 2-4, Dach 4-5
    und 5-3. Von Hand: Grade (1)=3, (2)=3, (3)=4, (4)=4, (5)=2 - genau 2 ungerade Knoten (1 und 2, die beiden unteren Ecken): ein **Eulerweg**, kein Eulerkreis, muss an einer der beiden unteren Ecken
    beginnen und an der anderen enden (der Kern des Kinderrätsels "ohne den Stift abzusetzen")."""
    xy = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.5, 1.8]], dtype=float)
    edges = [(0, 1), (1, 2), (2, 3), (0, 3), (0, 2), (1, 3), (3, 4), (2, 4)]
    return Instance(xy, tuple(sorted(edges)), "textbook", False, 0, TEXTBOOK_LABELS)
