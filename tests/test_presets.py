"""Presets: gültige Werte und jede Zahl der Hilfetexte gegen die echten Auswertungsfunktionen."""

import eul_constants as C
import eul_evaluation as ev
from eul_evaluation import Settings
from eul_presets import PRESET_KEYS, SETTING_SPECS


def _settings(name):
    p = C.PRESETS[name]
    return Settings(p["kind"], p.get("n", C.DEFAULT_N), p.get("n_cycles", C.DEFAULT_CYCLES), p.get("target", "circuit"), False, p.get("nettype", "grid"), p.get("side", C.DEFAULT_SIDE),
                     p.get("seed", C.DEFAULT_SEED), p.get("order", "fixed"))


def _has(name, *values):
    for v in values:
        assert v in C.PRESET_HELP[name], (name, v)


def test_every_preset_has_valid_values_and_a_help_text():
    assert list(C.PRESETS) == list(C.PRESET_HELP) and len(C.PRESETS) == 7
    for name, p in C.PRESETS.items():
        assert set(p) <= set(PRESET_KEYS) and {"kind", "step"} <= set(p) and p["step"] in C.STEPS
        for key, state_key in PRESET_KEYS.items():
            if key in p and state_key in SETTING_SPECS:
                spec = SETTING_SPECS[state_key]
                assert spec.caster(p[key]) == p[key], (name, key)
                if spec.lo is not None:
                    assert spec.lo <= p[key] <= spec.hi, (name, key)
        assert C.PRESET_HELP[name].strip()


def test_help_textbook_and_euler_circuit_path():
    a = ev.analyse(_settings("Haus vom Nikolaus (Lehrbuch)"))
    assert (a.n, a.m, a.odd_count, a.classification) == (5, 8, 2, "path")
    _has("Haus vom Nikolaus (Lehrbuch)", "5 Kreuzungen", "8 Straßen")

    a = ev.analyse(_settings("Eulerkreis (Standardfall)"))
    assert (a.n, a.m, a.odd_count, a.classification, a.hierholzer.steps, a.fleury.steps) == (16, 29, 0, "circuit", 88, 807)
    _has("Eulerkreis (Standardfall)", "16 Knoten", "29 Kanten", "88 Elementarschritte", "807")

    a = ev.analyse(_settings("Eulerweg (ein ungerades Paar)"))
    assert (a.m, a.odd_count, a.classification, a.hierholzer.steps, a.fleury.steps) == (28, 2, "path", 85, 718)
    _has("Eulerweg (ein ungerades Paar)", "28 statt 29", "85", "718")


def test_help_directed_and_city_presets():
    import eul_algorithm as ea
    import eul_scenario as es

    p = C.PRESETS["Gerichteter Eulerkreis"]
    inst = es.euler_instance(p["n"], p["n_cycles"], True, p["target"], p["seed"])
    adj = ea.adjacency_directed(inst.n, inst.edges)
    assert (inst.n, inst.m, ea.classify_directed(adj)) == (16, 38, "circuit")
    hr = ea.hierholzer_directed(adj)
    assert hr.steps == 115
    _has("Gerichteter Eulerkreis", "16 Knoten", "38 Bögen", "115 Elementarschritte")

    a = ev.analyse(_settings("Betriebsnetz (nicht eulersch)"))
    assert (a.n, a.m, a.odd_count, a.classification) == (64, 112, 24, "none")
    _has("Betriebsnetz (nicht eulersch)", "64 Knoten", "112 Straßen", "24 Kreuzungen")

    a = ev.analyse(_settings("Zufallsgraph (viele ungerade Knoten)"))
    assert (a.n, a.m, a.odd_count, a.classification) == (64, 112, 36, "none")
    _has("Zufallsgraph (viele ungerade Knoten)", "36 ungerade Knoten")


def test_help_cost_sweep_preset():
    rows = ev.cost_sweep(C.COST_NS)
    first, last = rows[0], rows[-1]
    assert (first["n"], first["hierholzer"], first["fleury"]) == (8, 55, 378)
    assert (last["n"], last["hierholzer"], last["fleury"]) == (60, 325, 9830)
    _has("Aufwand: Hierholzer gegen Fleury", "6.9-Fache", "30.2-Fache", "325 gegen 9830")
