"""Instanzen: Eulernetz (immer eulersch bzw. genau 2 ungerade), Betriebsnetz/Zufallsgraph (zusammenhängend), Haus vom Nikolaus (von Hand)."""

import networkx as nx
import pytest

import eul_algorithm as ea
import eul_scenario as es


def _degrees_undirected(inst):
    deg = [0] * inst.n
    for u, v in inst.edges:
        deg[u] += 1
        deg[v] += 1
    return deg


def test_euler_circuit_instances_have_all_even_degrees_and_are_connected():
    for seed in range(60):
        inst = es.euler_instance(n=14, n_cycles=4, directed=False, target="circuit", seed=seed)
        deg = _degrees_undirected(inst)
        assert all(d % 2 == 0 for d in deg), (seed, deg)
        adj = ea.adjacency(inst.n, inst.edges)
        assert ea.is_connected(adj)


def test_euler_path_instances_have_exactly_two_odd_degree_nodes():
    for seed in range(60):
        inst = es.euler_instance(n=14, n_cycles=4, directed=False, target="path", seed=seed)
        deg = _degrees_undirected(inst)
        assert sum(d % 2 for d in deg) == 2, (seed, deg)


def test_handshake_lemma_odd_count_is_always_even():
    for seed in range(30):
        inst = es.city_instance(side=6, nettype="random", seed=seed)
        deg = _degrees_undirected(inst)
        assert sum(d % 2 for d in deg) % 2 == 0


def test_directed_euler_circuit_instances_are_balanced():
    for seed in range(60):
        inst = es.euler_instance(n=10, n_cycles=3, directed=True, target="circuit", seed=seed)
        n = inst.n
        out_deg, in_deg = [0] * n, [0] * n
        for u, v in inst.edges:
            out_deg[u] += 1
            in_deg[v] += 1
        assert out_deg == in_deg, seed


def test_directed_euler_path_instances_have_one_plus_one_and_one_minus_one():
    for seed in range(60):
        inst = es.euler_instance(n=10, n_cycles=3, directed=True, target="path", seed=seed)
        n = inst.n
        out_deg, in_deg = [0] * n, [0] * n
        for u, v in inst.edges:
            out_deg[u] += 1
            in_deg[v] += 1
        diff = [o - i for o, i in zip(out_deg, in_deg)]
        assert diff.count(1) == 1 and diff.count(-1) == 1 and diff.count(0) == n - 2, (seed, diff)


def test_no_duplicate_or_self_loop_edges():
    for seed in range(30):
        for directed in (False, True):
            inst = es.euler_instance(n=12, n_cycles=4, directed=directed, target="circuit", seed=seed)
            assert len(set(inst.edges)) == len(inst.edges)
            assert all(u != v for u, v in inst.edges)


def test_city_and_random_are_connected_and_match_grid_edge_count():
    for seed in range(15):
        grid = es.city_instance(side=6, nettype="grid", seed=seed)
        rand = es.city_instance(side=6, nettype="random", seed=seed)
        assert grid.m == rand.m
        adj_g = ea.adjacency(grid.n, grid.edges)
        adj_r = ea.adjacency(rand.n, rand.edges)
        assert ea.is_connected(adj_g) and ea.is_connected(adj_r)


def test_grid_edge_count_matches_the_known_formula():
    inst = es.city_instance(side=6, nettype="grid", seed=1)
    side = 6
    assert inst.m == 2 * side * (side - 1)


def test_textbook_haus_vom_nikolaus_degrees_by_hand():
    inst = es.textbook_instance()
    assert inst.n == 5 and inst.m == 8
    deg = _degrees_undirected(inst)
    assert deg == [3, 3, 4, 4, 2]
    assert [i for i, d in enumerate(deg) if d % 2] == [0, 1]
    G = nx.Graph()
    G.add_nodes_from(range(5))
    G.add_edges_from(inst.edges)
    assert not nx.is_eulerian(G) and nx.has_eulerian_path(G)


def test_determinism_and_platform_independent_stream():
    for kind_call in (
        lambda: es.euler_instance(n=14, n_cycles=4, directed=False, target="circuit", seed=7),
        lambda: es.euler_instance(n=10, n_cycles=3, directed=True, target="path", seed=7),
        lambda: es.city_instance(side=6, nettype="random", seed=7),
    ):
        a, b = kind_call(), kind_call()
        assert a.edges == b.edges and (a.xy == b.xy).all()


def test_errors():
    with pytest.raises(ValueError):
        es.euler_instance(n=2)
    with pytest.raises(ValueError):
        es.euler_union_instance(10, 2, False, "nonsense", 1)
    with pytest.raises(ValueError):
        es.city_instance(side=6, nettype="nope")
    with pytest.raises(ValueError):
        es.city_instance(side=1)
