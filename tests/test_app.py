"""AppTest-Rauchtests: Voreinstellung, jedes Preset, jeder Schritt für jede Instanz, Tour-Schritt-Regler, Randwerte, Permalink-Grenzen, bedingte Regler, Berechnungen auf Abruf, Footer."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import eul_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(step=1, **state):
    at = AppTest.from_file(APP, default_timeout=300)
    state.setdefault("eul_step", step)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    return at


def _ok(at):
    assert not at.exception, [e.value for e in at.exception]


def _click(at, key):
    next(b for b in at.button if b.key == key).click().run()


def test_default_run_shows_the_summary():
    at = _run()
    _ok(at)
    assert {"Ungerade Knoten", "Klassifikation", "Aufwand Hierholzer", "Aufwand Fleury"} <= {m.label for m in at.metric}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_button_runs(name):
    at = _run(kind_select="euler")
    _click(at, f"preset_{name}")
    _ok(at)
    p, ss = C.PRESETS[name], at.session_state
    assert ss["kind_select"] == p["kind"] and ss["eul_step"] == p["step"]
    for key, state_key in (("n", "n_slider"), ("n_cycles", "cycles_slider"), ("target", "target_select"), ("side", "side_slider"), ("nettype", "nettype_select"), ("seed", "seed_input"),
                            ("order", "order_select")):
        if key in p:
            assert ss[state_key] == p[key], (name, key)


@pytest.mark.parametrize("step", [1, 2, 3, 4])
@pytest.mark.parametrize("kind", ["euler", "city", "textbook"])
def test_every_step_runs_for_every_kind(step, kind):
    at = _run(step=step, kind_select=kind, n_slider=10, side_slider=6)
    _ok(at)
    assert at.session_state["eul_step"] == step


@pytest.mark.parametrize("target", ["circuit", "path"])
def test_every_step_runs_for_both_targets(target):
    for step in (1, 2, 3, 4):
        _ok(_run(step=step, kind_select="euler", target_select=target))


@pytest.mark.parametrize("nettype", ["grid", "random"])
def test_city_runs_for_both_nettypes(nettype):
    for step in (1, 2, 3, 4):
        _ok(_run(step=step, kind_select="city", nettype_select=nettype))


@pytest.mark.parametrize("algo", ["hierholzer", "fleury"])
def test_tour_slider_every_position(algo):
    at = _run(step=1, kind_select="euler", n_slider=8, algo_select=algo)
    _ok(at)
    n_steps = at.session_state["tour_k"]
    for k in sorted({1, max(1, n_steps // 2), n_steps}):
        at2 = _run(step=1, kind_select="euler", n_slider=8, algo_select=algo, tour_k=k)
        _ok(at2)
        assert at2.session_state["tour_k"] == k


def test_step_one_reports_no_tour_when_classification_is_none():
    at = _run(step=1, kind_select="city", nettype_select="grid", side_slider=8)
    _ok(at)
    assert any("keine Eulertour" in i.value for i in at.info)


def test_permalink_values_are_clamped_and_invalid_choices_fall_back_to_the_default():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(kind="nope", n="9999", cycles="0", target="wheel", side="999", net="mesh", order="sorted", seed="-4", step="9").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert (ss["kind_select"], ss["n_slider"], ss["cycles_slider"], ss["target_select"], ss["side_slider"], ss["nettype_select"], ss["order_select"], ss["seed_input"], ss["eul_step"]) == (
        "euler", C.N_MAX, C.CYCLES_MIN, "circuit", C.SIDE_MAX, "grid", "fixed", 0, 1)


def test_permalink_accepts_valid_values_and_writes_them_back():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(kind="city", side="9", net="random", order="shuffled", seed="7", step="2").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert (ss["side_slider"], ss["nettype_select"], ss["order_select"], ss["seed_input"], ss["eul_step"]) == (9, "random", "shuffled", 7, 2)
    assert at.query_params["net"] in (["random"], "random") and at.query_params["step"] in (["2"], "2")
    assert ss["side_widget"] == 9 and ss["seed_widget"] == 7


def test_sidebar_shows_the_controls_that_belong_to_the_instance():
    euler = _run(kind_select="euler")
    assert any(w.key == "n_widget" for w in euler.slider) and any(r.key == "target_select" for r in euler.radio)
    city = _run(kind_select="city")
    assert any(w.key == "side_widget" for w in city.slider) and any(r.key == "nettype_widget" for r in city.radio)
    book = _run(kind_select="textbook")
    assert not any(w.key == "n_widget" for w in book.slider) and not any(w.key == "side_widget" for w in book.slider)
    assert any(r.key == "order_select" for r in book.radio)


def test_switching_kind_back_and_forth_keeps_the_stored_values():
    at = _run(kind_select="euler", n_slider=20, cycles_slider=5, seed_input=11)
    at.session_state["kind_select"] = "city"
    at.run()
    _ok(at)
    at.session_state["kind_select"] = "euler"
    at.run()
    _ok(at)
    assert at.session_state["n_widget"] == 20 and at.session_state["cycles_widget"] == 5


def test_dice_button_changes_the_seed_and_the_visible_widget():
    at = _run(kind_select="euler")
    old = at.session_state["seed_input"]
    next(b for b in at.button if b.label == "🎲 Neue Instanz generieren").click().run()
    _ok(at)
    assert at.session_state["seed_input"] != old and at.session_state["seed_widget"] == at.session_state["seed_input"]


def test_on_demand_experiments():
    at = _run(step=4)
    _click(at, "cost_start")
    assert len(at.get("plotly_chart")) >= 1
    _click(at, "share_start")
    _ok(at)
    assert len(at.get("plotly_chart")) >= 3


@pytest.mark.parametrize("kw", [dict(n_slider=C.N_MIN), dict(n_slider=C.N_MAX), dict(side_slider=C.SIDE_MIN), dict(side_slider=C.SIDE_MAX), dict(cycles_slider=C.CYCLES_MIN),
                                 dict(cycles_slider=C.CYCLES_MAX)])
def test_extreme_settings_run_on_every_step(kw):
    kind = "city" if "side_slider" in kw else "euler"
    for step in (1, 2, 3, 4):
        _ok(_run(step=step, kind_select=kind, **kw))


def test_footer_limits_and_literature_are_present():
    at = _run()
    assert any("Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net)" in c.value for c in at.caption)
    assert any("Wo die Annahmen enden" in s.value for s in at.subheader)
    assert any("Hierholzer" in m.value and "Fleury" in m.value for e in at.expander for m in e.markdown)
