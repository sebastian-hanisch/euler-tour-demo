"""Auswertung: Settings/analyse-Konsistenz, Sweeps."""

import eul_algorithm as ea
import eul_constants as C
import eul_evaluation as ev
import eul_scenario as es
from eul_evaluation import Settings


def test_analyse_matches_direct_computation_for_each_kind():
    for kind_settings in (
        Settings("euler", 14, 3, "circuit", seed=7),
        Settings("euler", 14, 3, "path", seed=7),
        Settings("city", nettype="grid", side=6, seed=7),
        Settings("city", nettype="random", side=6, seed=7),
        Settings("textbook"),
    ):
        a = ev.analyse(kind_settings)
        if kind_settings.kind == "textbook":
            inst = es.textbook_instance()
        elif kind_settings.kind == "euler":
            inst = es.euler_instance(kind_settings.n, kind_settings.n_cycles, False, kind_settings.target, kind_settings.seed)
        else:
            inst = es.city_instance(kind_settings.side, kind_settings.nettype, kind_settings.seed)
        adj = ea.adjacency(inst.n, inst.edges, kind_settings.order, kind_settings.seed)
        assert a.n == inst.n and a.m == inst.m
        assert a.odd_count == len(ea.odd_nodes(adj))
        assert a.classification == ea.classify(adj)


def test_run_config_length_and_directed_analysis_only_for_directed_settings():
    rows = ev.run_config(Settings("euler", 12, 3, "circuit", seed=1))
    assert len(rows) == len(C.SWEEP_SEEDS)
    for r in rows:
        assert not r.directed and r.hierholzer is not None and r.fleury is not None


def test_cost_sweep_is_monotone_increasing_in_n():
    rows = ev.cost_sweep((8, 16, 24, 32))
    hs = [r["hierholzer"] for r in rows]
    fs = [r["fleury"] for r in rows]
    assert hs == sorted(hs)
    assert fs == sorted(fs)
    assert all(r["ratio"] > 1 for r in rows)


def test_eulerian_share_sweep_shape_and_bounds():
    rows = ev.eulerian_share_sweep("grid", (2, 4, 6), seeds=range(100000, 100020))
    for r in rows:
        total = r["share_circuit"] + r["share_path"] + r["share_none"]
        assert abs(total - 1.0) < 1e-9
        assert 0 <= r["share_circuit"] <= 1 and 0 <= r["share_path"] <= 1 and 0 <= r["share_none"] <= 1


def test_eulerian_share_sweep_decays_to_near_zero_for_larger_grids():
    rows = ev.eulerian_share_sweep("grid", (2, 6), seeds=range(100000, 100050))
    small, big = rows[0], rows[1]
    assert small["share_circuit"] + small["share_path"] > big["share_circuit"] + big["share_path"]
