"""Jede Zahl aus README und Konstanten-Kommentar, nachgerechnet über die echten Auswertungsfunktionen."""

from functools import lru_cache

import eul_constants as C
import eul_evaluation as ev


@lru_cache(maxsize=None)
def _cost():
    return ev.cost_sweep(C.COST_NS)


@lru_cache(maxsize=None)
def _share(nettype):
    return {r["side"]: r for r in ev.eulerian_share_sweep(nettype, C.SHARE_SIDES, seeds=C.SHARE_SEEDS)}


def test_cost_sweep_values_over_n():
    rows = _cost()
    ns = [r["n"] for r in rows]
    assert ns == list(C.COST_NS)
    hs = [r["hierholzer"] for r in rows]
    fs = [r["fleury"] for r in rows]
    assert hs == [55, 88, 112, 154, 187, 268, 325]
    assert fs == [378, 927, 1441, 2821, 3728, 7989, 9830]


def test_cost_ratio_grows_from_about_seven_to_about_thirty():
    rows = _cost()
    assert round(rows[0]["ratio"], 1) == 6.9
    assert round(rows[-1]["ratio"], 1) == 30.2


def test_grid_side_two_is_always_a_circuit_side_four_never_eulerian():
    grid = _share("grid")
    assert grid[2]["share_circuit"] == 1.0
    assert grid[4]["share_circuit"] == grid[4]["share_path"] == 0.0


def test_random_side_two_is_always_eulerian_side_four_never():
    rnd = _share("random")
    assert rnd[2]["share_circuit"] + rnd[2]["share_path"] == 1.0
    assert round(rnd[2]["share_circuit"], 2) == 0.35 and round(rnd[2]["share_path"], 2) == 0.65
    assert rnd[4]["share_circuit"] == rnd[4]["share_path"] == 0.0


def test_directed_hierholzer_steps_on_the_preset_instance():
    import eul_algorithm as ea
    import eul_scenario as es

    inst = es.euler_instance(16, 3, True, "circuit", 35)
    adj = ea.adjacency_directed(inst.n, inst.edges)
    hr = ea.hierholzer_directed(adj)
    assert (inst.m, hr.steps) == (38, 115)
