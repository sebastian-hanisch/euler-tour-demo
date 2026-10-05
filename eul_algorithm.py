"""Eulertouren: Hierholzer (Kreise verschmelzen, O(n+m)) gegen Fleury (schrittweise, meidet Brücken im Restgraphen - braucht Tarjans Low-Link aus der Brücken-Demo bei JEDEM Schritt, O(m*(n+m))).

**Elementarschritte** (das Aufwandsmaß dieser Reihe, keine Laufzeit): jeder abgearbeitete Knoten und jede von einem Ende angesehene Kante zählt 1, wie in den Geschwister-Demos.

Begriffe: ein **Eulerkreis** besucht jede Kante genau einmal und kehrt zum Start zurück (existiert genau dann, wenn der ganze Graph zusammenhängend ist - ein isolierter Knoten stört, Konvention wie networkx, obwohl ein Zug über alle Kanten auch dann existierte - und jeder Knoten
geraden Grad hat); ein **Eulerweg** tut dasselbe ohne Rückkehr (existiert genau dann, wenn zusätzlich genau 0 oder 2 Knoten ungeraden Grad haben; bei 2 ungeraden Knoten muss der Weg an einem beginnen
und am anderen enden). Die Zahl der ungeraden Knoten ist nach dem Handschlaglemma immer gerade."""

import random
from collections import deque
from dataclasses import dataclass, field


def adjacency(n, edges, order="fixed", seed=0):
    """Adjazenzliste aus ungerichteten Kanten (u, v, ...); "fixed" = aufsteigende Nachbarn, "shuffled" = je Knoten gemischt (Seed fest, Python-`random`)."""
    adj = [[] for _ in range(n)]
    for e in edges:
        u, v = int(e[0]), int(e[1])
        adj[u].append(v)
        adj[v].append(u)
    for lst in adj:
        lst.sort()
    if order == "shuffled":
        rng = random.Random(int(seed) * 1_000_003 + 5150)
        for lst in adj:
            rng.shuffle(lst)
    elif order != "fixed":
        raise ValueError(f"unbekannte Reihenfolge {order}")
    return adj


def adjacency_directed(n, arcs, order="fixed", seed=0):
    """Adjazenzliste aus gerichteten Bögen (u, v): adj[u] enthält v für jeden Bogen u -> v."""
    adj = [[] for _ in range(n)]
    for u, v in arcs:
        adj[int(u)].append(int(v))
    for lst in adj:
        lst.sort()
    if order == "shuffled":
        rng = random.Random(int(seed) * 1_000_003 + 5150)
        for lst in adj:
            rng.shuffle(lst)
    elif order != "fixed":
        raise ValueError(f"unbekannte Reihenfolge {order}")
    return adj


def degrees(adj):
    return [len(lst) for lst in adj]


def odd_nodes(adj):
    """Knoten ungeraden Grades, aufsteigend. Ihre Zahl ist nach dem Handschlaglemma immer gerade."""
    return [v for v, d in enumerate(degrees(adj)) if d % 2 == 1]


def is_connected(adj):
    """True, wenn der GANZE Graph zusammenhängend ist (auch isolierte Knoten müssen es sein - genau networkx' `is_eulerian`-Konvention, gegen networkx getestet statt angenommen: ein isolierter
    Knoten macht einen sonst eulerschen Graphen NICHT eulersch, obwohl er nie besucht werden müsste)."""
    n = len(adj)
    if n <= 1:
        return True
    seen = [False] * n
    seen[0] = True
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                queue.append(v)
    return all(seen)


def classify(adj):
    """"circuit" (Eulerkreis: 0 ungerade Knoten, ganzer Graph zusammenhängend), "path" (Eulerweg: genau 2 ungerade Knoten, zusammenhängend) oder "none"."""
    if not is_connected(adj):
        return "none"
    k = len(odd_nodes(adj))
    if k == 0:
        return "circuit"
    if k == 2:
        return "path"
    return "none"


def _weakly_connected(adj_out, adj_in):
    n = len(adj_out)
    if n <= 1:
        return True
    seen = [False] * n
    seen[0] = True
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adj_out[u] + adj_in[u]:
            if not seen[v]:
                seen[v] = True
                queue.append(v)
    return all(seen)


def directed_is_connected(adj_out):
    """Der zugrunde liegende ungerichtete Graph (der GANZE, auch isolierte Knoten) ist zusammenhängend."""
    n = len(adj_out)
    adj_in = [[] for _ in range(n)]
    for u in range(n):
        for v in adj_out[u]:
            adj_in[v].append(u)
    return _weakly_connected(adj_out, adj_in)


def classify_directed(adj_out):
    """Für gerichtete Graphen: "circuit", wenn Eingangsgrad == Ausgangsgrad an jedem Knoten UND der zugrunde liegende ungerichtete Graph (der GANZE, auch isolierte Knoten - wie im ungerichteten Fall
    gegen networkx getestet) zusammenhängend ist, sonst "none". (Eulerwege in gerichteten Graphen - genau ein Knoten mit Ausgangsgrad - Eingangsgrad = 1 und einer mit -1, alle übrigen ausgeglichen -
    werden hier NICHT unterschieden, siehe Grenzen.)"""
    n = len(adj_out)
    adj_in = [[] for _ in range(n)]
    for u in range(n):
        for v in adj_out[u]:
            adj_in[v].append(u)
    out_deg = [len(lst) for lst in adj_out]
    in_deg = [len(lst) for lst in adj_in]
    if out_deg != in_deg:
        return "none"
    if not _weakly_connected(adj_out, adj_in):
        return "none"
    return "circuit"


# --- Hierholzer ------------------------------------------------------------------------------------------------------------------------------------


@dataclass
class EulerResult:
    tour: list                                    # Knotenfolge (Länge m + 1 bei Erfolg)
    steps: int
    events: list = field(default_factory=list)    # ("visit", Knoten) je Schritt in der Reihenfolge der endgültigen Tour
    method: str = ""
    bridge_calls: int = 0                         # nur Fleury: Zahl der Low-Link-Aufrufe


def hierholzer(adj, start=None):
    """Iterativ: von `start` aus einem unbenutzten Nachbarn folgen, bis kein unbenutzter mehr da ist; dann rückwärts über den Stapel Teilkreise an der Stelle einfügen, an der ein Knoten noch unbenutzte
    Kanten hat (die klassische Verschmelzung, Hierholzer 1873). Kanten werden über ein Nutzungs-Array je gerichteter Kopie markiert (Kante u-v einmal von u, einmal von v aus). Aufwand O(n + m).
    Ohne `start`: bei einem Eulerweg (genau 2 ungerade Knoten) MUSS an einem der beiden begonnen werden - sonst bleibt die Suche in einem Teilkreis stecken, der nie zum Start zurückkehrt (der klassische
    Fallstrick); sonst der erste Knoten mit Grad > 0."""
    n = len(adj)
    if start is None:
        odds = odd_nodes(adj)
        start = odds[0] if odds else next((v for v in range(n) if adj[v]), 0)
    pos = [0] * n
    used = [[False] * len(adj[v]) for v in range(n)]
    steps = 0
    stack = [start]
    tour = []
    while stack:
        u = stack[-1]
        steps += 1
        while pos[u] < len(adj[u]) and used[u][pos[u]]:
            pos[u] += 1
        if pos[u] == len(adj[u]):
            tour.append(stack.pop())
            continue
        v = adj[u][pos[u]]
        used[u][pos[u]] = True
        j = adj[v].index(u, 0)
        while used[v][j]:
            j = adj[v].index(u, j + 1)
        used[v][j] = True
        pos[u] += 1
        steps += 1
        stack.append(v)
    tour.reverse()
    events = [("visit", v) for v in tour]
    return EulerResult(tour, steps, events, "hierholzer")


def hierholzer_directed(adj_out, start=None):
    """Wie `hierholzer`, aber für gerichtete Graphen: einfachere Buchführung, da jeder Bogen nur von seinem Startknoten aus konsumiert wird (kein Partner-Index nötig). Ohne `start`: bei einem
    gerichteten Eulerweg (ein Knoten mit Ausgangsgrad - Eingangsgrad = +1) MUSS dort begonnen werden, sonst der erste Knoten mit Ausgangsgrad > 0."""
    n = len(adj_out)
    if start is None:
        in_deg = [0] * n
        for u in range(n):
            for v in adj_out[u]:
                in_deg[v] += 1
        plus_ones = [v for v in range(n) if len(adj_out[v]) - in_deg[v] == 1]
        start = plus_ones[0] if plus_ones else next((v for v in range(n) if adj_out[v]), 0)
    pos = [0] * n
    steps = 0
    stack = [start]
    tour = []
    while stack:
        u = stack[-1]
        steps += 1
        if pos[u] < len(adj_out[u]):
            v = adj_out[u][pos[u]]
            pos[u] += 1
            steps += 1
            stack.append(v)
        else:
            tour.append(stack.pop())
    tour.reverse()
    events = [("visit", v) for v in tour]
    return EulerResult(tour, steps, events, "hierholzer")


# --- Low-Link (wortgleiche Kopie aus der Brücken-Demo, brg_algorithm.low_link) ----------------------------------------------------------------------


def _key(u, v):
    return (u, v) if u < v else (v, u)


@dataclass
class LowLink:
    disc: list
    low: list
    parent: list
    root: list
    size: list
    bridges: list = field(default_factory=list)
    articulation: set = field(default_factory=set)
    steps: int = 0


def low_link(adj):
    """Tarjans Low-Link, iterativ (Kopie aus `brg_algorithm.py`, ohne Blöcke - hier werden nur die Brücken gebraucht): Baumkante (p, u) ist Brücke, wenn low[u] > disc[p]."""
    n = len(adj)
    disc, low, parent, root, size = [0] * n, [0] * n, [-1] * n, [-1] * n, [1] * n
    r = LowLink(disc, low, parent, root, size)
    clock = 0
    pos = [0] * n
    for s in range(n):
        if disc[s]:
            continue
        clock += 1
        disc[s] = low[s] = clock
        root[s] = s
        r.steps += 1
        stack = [s]
        while stack:
            u = stack[-1]
            if pos[u] < len(adj[u]):
                v = adj[u][pos[u]]
                pos[u] += 1
                r.steps += 1
                if not disc[v]:
                    parent[v] = u
                    root[v] = s
                    clock += 1
                    disc[v] = low[v] = clock
                    r.steps += 1
                    stack.append(v)
                elif v != parent[u] and disc[v] < disc[u]:
                    if disc[v] < low[u]:
                        low[u] = disc[v]
            else:
                stack.pop()
                p = parent[u]
                if p != -1:
                    size[p] += size[u]
                    if low[u] < low[p]:
                        low[p] = low[u]
                    if low[u] > disc[p]:
                        r.bridges.append(_key(p, u))
    return r


# --- Fleury ------------------------------------------------------------------------------------------------------------------------------------------


def fleury(adj, start=None):
    """Schrittweise: vom aktuellen Knoten aus wird eine Kante gewählt, die im Restgraphen (nur unbenutzte Kanten) KEINE Brücke ist, sofern es eine solche Alternative gibt (kleinster Nachbar bei
    Gleichstand); nur wenn jede verbleibende Kante vom aktuellen Knoten aus eine Brücke ist (typischerweise die einzige), wird sie überquert. Der Brückentest (`low_link`) wird bei JEDEM Schritt auf dem
    kompletten Restgraphen neu berechnet - deutlich teurer als Hierholzers einmaliger Durchlauf, aber ebenfalls stets O(n + m) je Aufruf, macht insgesamt O(m*(n+m))."""
    n = len(adj)
    remaining = [set(lst) for lst in adj]
    # Multikanten (parallele Kanten, hier nicht erzeugt, aber der Vollständigkeit halber): jede Kante wird als (Nachbarmenge) geführt, ein einzelner Grad-2-Fall zwischen denselben zwei Knoten würde
    # kollabieren - die Instanzen dieser Demo sind einfache Graphen, daher unkritisch (siehe Grenzen).
    if start is None:
        odds = odd_nodes(adj)
        start = odds[0] if odds else next((v for v in range(n) if adj[v]), 0)
    steps = 0
    bridge_calls = 0
    u = start
    tour = [u]
    events = []
    total_edges = sum(len(s) for s in remaining) // 2
    for _ in range(total_edges):
        neighbors = sorted(remaining[u])
        if not neighbors:
            break
        if len(neighbors) == 1:
            v = neighbors[0]
            had_alternative, crossed_bridge = False, True
        else:
            resid_adj = [sorted(remaining[x]) for x in range(n)]
            ll = low_link(resid_adj)
            bridge_calls += 1
            steps += ll.steps
            bridge_set = set(ll.bridges)
            non_bridge = [w for w in neighbors if _key(u, w) not in bridge_set]
            v = non_bridge[0] if non_bridge else neighbors[0]
            had_alternative = bool(non_bridge)
            crossed_bridge = v not in non_bridge
        remaining[u].discard(v)
        remaining[v].discard(u)
        steps += 1
        events.append(("step", u, v, had_alternative, crossed_bridge))
        u = v
        tour.append(u)
    return EulerResult(tour, steps, events, "fleury", bridge_calls)
