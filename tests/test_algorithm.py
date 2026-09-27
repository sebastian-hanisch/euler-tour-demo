"""Zentrale Korrektheits-Kette: Hierholzer/Fleury (ungerichtet und gerichtet) gegen networkx, Klassifikation inkl. Fallstrick "gerade Grade aber unzusammenhängend", Handschlaglemma,
Haus vom Nikolaus von Hand, Buchführung, Sonderfälle."""

import networkx as nx
import pytest

import eul_algorithm as ea
import eul_scenario as es


def _tour_edges_ok(edges, tour, directed=False):
    """Jede Kante des Tours wird genau einmal benutzt, und die Menge der benutzten Kanten ist genau die Kantenmenge der Instanz."""
    used = set()
    for i in range(len(tour) - 1):
        e = (tour[i], tour[i + 1]) if directed else ea._key(tour[i], tour[i + 1])
        if e in used:
            return False
        used.add(e)
    want = set(edges) if directed else {ea._key(u, v) for u, v in edges}
    return used == want


# --- 1/3: Hierholzer und Fleury (ungerichtet) == networkx --------------------------------------------------------------------------------------


@pytest.mark.parametrize("target", ["circuit", "path"])
@pytest.mark.parametrize("kind", ["euler", "textbook"])
def test_hierholzer_and_fleury_match_networkx(kind, target):
    checked = 0
    for seed in range(120):
        if kind == "textbook":
            if seed > 0:
                break
            inst = es.textbook_instance()
        else:
            inst = es.euler_instance(n=14, n_cycles=4, directed=False, target=target, seed=seed)
        adj = ea.adjacency(inst.n, inst.edges)
        cls = ea.classify(adj)
        G = nx.Graph()
        G.add_nodes_from(range(inst.n))
        G.add_edges_from(inst.edges)
        nx_cls = "circuit" if nx.is_eulerian(G) else ("path" if nx.has_eulerian_path(G) else "none")
        assert cls == nx_cls, (kind, target, seed, cls, nx_cls)
        if cls == "none":
            continue
        checked += 1
        hr = ea.hierholzer(adj)
        assert len(hr.tour) == inst.m + 1
        assert _tour_edges_ok(inst.edges, hr.tour)
        fr = ea.fleury(adj)
        assert len(fr.tour) == inst.m + 1
        assert _tour_edges_ok(inst.edges, fr.tour)
        odd = set(ea.odd_nodes(adj))
        if cls == "circuit":
            assert hr.tour[0] == hr.tour[-1] and fr.tour[0] == fr.tour[-1]
        else:
            assert {hr.tour[0], hr.tour[-1]} == odd
            assert {fr.tour[0], fr.tour[-1]} == odd
    assert checked > 0


def test_hierholzer_matches_networkx_on_city_and_random_when_eulerian():
    checked = 0
    for nettype in ("grid", "random"):
        for seed in range(30):
            inst = es.city_instance(side=6, nettype=nettype, seed=seed)
            adj = ea.adjacency(inst.n, inst.edges)
            cls = ea.classify(adj)
            G = nx.Graph()
            G.add_nodes_from(range(inst.n))
            G.add_edges_from(inst.edges)
            nx_cls = "circuit" if nx.is_eulerian(G) else ("path" if nx.has_eulerian_path(G) else "none")
            assert cls == nx_cls, (nettype, seed, cls, nx_cls)
            if cls != "none":
                checked += 1
                r = ea.hierholzer(adj)
                assert _tour_edges_ok(inst.edges, r.tour)


# --- 2: Hierholzer (gerichtet) == networkx --------------------------------------------------------------------------------------------------


def test_hierholzer_directed_matches_networkx():
    checked = 0
    for seed in range(120):
        inst = es.euler_instance(n=10, n_cycles=3, directed=True, target="circuit", seed=seed)
        adj = ea.adjacency_directed(inst.n, inst.edges)
        cls = ea.classify_directed(adj)
        D = nx.DiGraph()
        D.add_nodes_from(range(inst.n))
        D.add_edges_from(inst.edges)
        assert cls == ("circuit" if nx.is_eulerian(D) else "none"), seed
        if cls == "circuit":
            checked += 1
            r = ea.hierholzer_directed(adj)
            assert len(r.tour) == inst.m + 1
            assert _tour_edges_ok(inst.edges, r.tour, directed=True)
            assert r.tour[0] == r.tour[-1]
    assert checked > 0


def test_classify_directed_none_on_unbalanced_or_disconnected():
    # unbalanced: a single arc leaves one node with out-in=1 and one with -1
    adj = ea.adjacency_directed(4, [(0, 1), (1, 2), (2, 0), (2, 3)])
    assert ea.classify_directed(adj) == "none"
    # balanced but weakly disconnected (two separate directed triangles)
    adj2 = ea.adjacency_directed(6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)])
    assert ea.classify_directed(adj2) == "none"
    D = nx.DiGraph()
    D.add_nodes_from(range(6))
    D.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)])
    assert not nx.is_eulerian(D)


# --- 4: Klassifikations-Fallstrick "gerade Grade, aber unzusammenhängend" --------------------------------------------------------------------


def test_even_degrees_but_disconnected_is_not_eulerian():
    """Klassischer Fallstrick: alle Grade gerade heißt NICHT automatisch eulersch, wenn der Graph (oder ein isolierter Knoten) unzusammenhängend ist."""
    edges = ((0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3))
    adj = ea.adjacency(6, edges)
    assert all(d % 2 == 0 for d in ea.degrees(adj))
    assert ea.classify(adj) == "none"
    G = nx.Graph()
    G.add_nodes_from(range(6))
    G.add_edges_from(edges)
    assert not nx.is_eulerian(G) and not nx.has_eulerian_path(G)


def test_isolated_node_breaks_an_otherwise_eulerian_graph():
    """Ein Knoten ganz ohne Kante macht den GANZEN Graphen nicht eulersch - genau networkx' `is_eulerian`-Konvention, gegen networkx bestätigt statt angenommen."""
    edges = ((0, 1), (1, 2), (2, 0))
    adj = ea.adjacency(4, edges)  # Knoten 3 ist isoliert
    assert ea.classify(adj) == "none"
    G = nx.Graph()
    G.add_nodes_from(range(4))
    G.add_edges_from(edges)
    assert not nx.is_eulerian(G)
    # ohne den isolierten Knoten ist derselbe Kantensatz sehr wohl ein Eulerkreis
    adj3 = ea.adjacency(3, edges)
    assert ea.classify(adj3) == "circuit"


# --- 5: Handschlaglemma ------------------------------------------------------------------------------------------------------------------------


def test_odd_node_count_is_always_even():
    for seed in range(30):
        inst = es.city_instance(side=6, nettype="random", seed=seed)
        adj = ea.adjacency(inst.n, inst.edges)
        assert len(ea.odd_nodes(adj)) % 2 == 0


def test_is_connected_matches_networkx():
    for seed in range(20):
        inst = es.city_instance(side=6, nettype="random", seed=seed)
        adj = ea.adjacency(inst.n, inst.edges)
        G = nx.Graph()
        G.add_nodes_from(range(inst.n))
        G.add_edges_from(inst.edges)
        assert ea.is_connected(adj) == nx.is_connected(G)


# --- 6: Haus vom Nikolaus von Hand -------------------------------------------------------------------------------------------------------------


def test_haus_vom_nikolaus_by_hand():
    inst = es.textbook_instance()
    adj = ea.adjacency(inst.n, inst.edges)
    assert ea.degrees(adj) == [3, 3, 4, 4, 2]
    assert ea.odd_nodes(adj) == [0, 1]
    assert ea.classify(adj) == "path"
    r = ea.hierholzer(adj)
    assert len(r.tour) == 9
    assert {r.tour[0], r.tour[-1]} == {0, 1}


# --- 7: Buchführung ----------------------------------------------------------------------------------------------------------------------------


def test_hierholzer_step_bookkeeping():
    inst = es.euler_instance(n=14, n_cycles=4, directed=False, target="circuit", seed=3)
    adj = ea.adjacency(inst.n, inst.edges)
    r = ea.hierholzer(adj)
    assert r.steps > 0
    assert len(r.events) == len(r.tour)


def test_fleury_bridge_calls_and_invariant():
    inst = es.euler_instance(n=14, n_cycles=4, directed=False, target="circuit", seed=3)
    adj = ea.adjacency(inst.n, inst.edges)
    r = ea.fleury(adj)
    assert r.bridge_calls > 0
    assert len(r.events) == inst.m
    for _, u, v, had_alternative, crossed_bridge in r.events:
        if had_alternative:
            assert not crossed_bridge, (u, v)


def test_neighbor_order_does_not_change_existence_or_classification():
    for seed in range(20):
        inst = es.euler_instance(n=12, n_cycles=3, directed=False, target="path", seed=seed)
        fixed = ea.adjacency(inst.n, inst.edges, order="fixed")
        shuffled = ea.adjacency(inst.n, inst.edges, order="shuffled", seed=seed)
        assert ea.classify(fixed) == ea.classify(shuffled)
        r1 = ea.hierholzer(fixed)
        r2 = ea.hierholzer(shuffled)
        assert len(r1.tour) == len(r2.tour) == inst.m + 1


def test_determinism():
    inst = es.euler_instance(n=14, n_cycles=4, directed=False, target="path", seed=5)
    adj = ea.adjacency(inst.n, inst.edges)
    r1, r2 = ea.hierholzer(adj), ea.hierholzer(adj)
    assert r1.tour == r2.tour
    f1, f2 = ea.fleury(adj), ea.fleury(adj)
    assert f1.tour == f2.tour and f1.steps == f2.steps


# --- 8: Sonderfälle ------------------------------------------------------------------------------------------------------------------------------


def test_single_cycle_is_trivial_for_hierholzer():
    edges = ((0, 1), (1, 2), (0, 2))
    adj = ea.adjacency(3, edges)
    assert ea.classify(adj) == "circuit"
    r = ea.hierholzer(adj)
    assert len(r.tour) == 4 and r.tour[0] == r.tour[-1]


def test_empty_graph_is_trivially_connected_and_circuit():
    adj = ea.adjacency(1, [])
    assert ea.is_connected(adj)
    assert ea.classify(adj) == "circuit"
    r = ea.hierholzer(adj)
    assert r.tour == [0]


def test_adjacency_invalid_order_raises():
    with pytest.raises(ValueError):
        ea.adjacency(3, [(0, 1)], order="nope")
    with pytest.raises(ValueError):
        ea.adjacency_directed(3, [(0, 1)], order="nope")


def test_low_link_bridges_match_bridges_demo_style_reference():
    """Die kopierte `low_link` findet auf einem Dreieck keine Brücke und auf einem Pfad jede Kante als Brücke (dieselben Invarianten wie in der Brücken-Demo)."""
    tri = ea.adjacency(3, [(0, 1), (1, 2), (0, 2)])
    assert ea.low_link(tri).bridges == []
    path = ea.adjacency(4, [(0, 1), (1, 2), (2, 3)])
    ll = ea.low_link(path)
    assert set(ll.bridges) == {(0, 1), (1, 2), (2, 3)}
