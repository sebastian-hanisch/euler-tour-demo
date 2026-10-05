"""Unabhängiges Orakel: Existenz von Eulerkreis/-weg per vollständiger Suche über alle Kantenzüge (kleine Zufallsgraphen, ungerichtet und gerichtet) gegen die Klassifikation der Demo;
Hierholzer und Fleury müssen einen gültigen Kantenzug liefern (jede Kante genau einmal, Kreis kehrt zurück, Weg beginnt/endet an den zwei ungeraden Knoten). Konvention der Demo (wie networkx):
ein isolierter Knoten macht den GANZEN Graphen nicht eulersch, obwohl ein Zug über alle Kanten existierte."""

import itertools
import random

import eul_algorithm as ea


def _brute(edges, directed):
    m = len(edges)
    if m == 0:
        return {"circuit"}
    inc = {}
    for i, (u, v) in enumerate(edges):
        inc.setdefault(u, []).append((i, v))
        if not directed:
            inc.setdefault(v, []).append((i, u))
    kinds = set()
    used = [False] * m

    def dfs(u, cnt, start):
        if cnt == m:
            kinds.add("circuit" if u == start else "path")
            return
        for i, v in inc.get(u, []):
            if not used[i]:
                used[i] = True
                dfs(v, cnt + 1, start)
                used[i] = False

    for s in sorted(inc):
        dfs(s, 0, s)
    return kinds


def _valid(tour, edges, directed):
    if len(tour) != len(edges) + 1:
        return False
    got = [(tour[i], tour[i + 1]) for i in range(len(edges))]
    if not directed:
        got = [tuple(sorted(e)) for e in got]
        edges = [tuple(sorted(e)) for e in edges]
    return sorted(got) == sorted(edges)


def test_undirected_classification_and_tours_against_exhaustive_search():
    rng = random.Random(3)
    for it in range(250):
        n = rng.randrange(1, 9)
        pairs = list(itertools.combinations(range(n), 2))
        rng.shuffle(pairs)
        edges = sorted(pairs[:rng.randrange(1, min(len(pairs), 12) + 1)]) if pairs else []
        if not edges:
            continue
        adj = ea.adjacency(n, edges, "shuffled" if it % 2 else "fixed", seed=it)
        kinds = _brute(edges, False)
        truth = "circuit" if "circuit" in kinds else ("path" if "path" in kinds else "none")
        isolated = any(not adj[v] for v in range(n))
        cls = ea.classify(adj)
        assert cls == ("none" if isolated else truth), (n, edges, cls, truth)
        if cls != "none":
            for res in (ea.hierholzer(adj), ea.fleury(adj)):
                assert _valid(res.tour, edges, False), (res.method, n, edges, res.tour)
                closed = res.tour[0] == res.tour[-1]
                assert closed == (cls == "circuit")
                if cls == "path":
                    assert sorted([res.tour[0], res.tour[-1]]) == ea.odd_nodes(adj)


def test_directed_classification_and_hierholzer_against_exhaustive_search():
    rng = random.Random(4)
    for it in range(250):
        n = rng.randrange(2, 7)
        arcs_all = [(u, v) for u in range(n) for v in range(n) if u != v]
        rng.shuffle(arcs_all)
        arcs = sorted(arcs_all[:rng.randrange(1, min(len(arcs_all), 10) + 1)])
        adj = ea.adjacency_directed(n, arcs, "shuffled" if it % 2 else "fixed", seed=it)
        isolated = any(not adj[v] and not any(v in lst for lst in adj) for v in range(n))
        truth = "circuit" if "circuit" in _brute(arcs, True) else "none"
        cls = ea.classify_directed(adj)
        assert cls == ("none" if isolated else truth), (n, arcs, cls, truth)
        if cls == "circuit":
            res = ea.hierholzer_directed(adj)
            assert _valid(res.tour, arcs, True) and res.tour[0] == res.tour[-1]
