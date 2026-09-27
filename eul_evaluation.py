"""Auswertung: Klassifikation, Hierholzer/Fleury, Aufwand über die Größe, Anteil eulerscher Zufallsgraphen/Betriebsnetze."""

from dataclasses import dataclass

import eul_algorithm as ea
import eul_constants as C
import eul_scenario as es


@dataclass
class Settings:
    kind: str = "euler"          # "euler" | "city" | "textbook"
    n: int = C.DEFAULT_N
    n_cycles: int = C.DEFAULT_CYCLES
    target: str = "circuit"
    directed: bool = False
    nettype: str = "grid"
    side: int = C.DEFAULT_SIDE
    seed: int = C.DEFAULT_SEED
    order: str = "fixed"


@dataclass
class Analysis:
    n: int
    m: int
    directed: bool
    classification: str
    odd_count: int
    hierholzer: object = None
    fleury: object = None
    ratio: float = None                 # Fleury-Schritte / Hierholzer-Schritte, nur wenn beide existieren


def _instance(settings):
    if settings.kind == "textbook":
        return es.textbook_instance()
    if settings.kind == "euler":
        return es.euler_instance(settings.n, settings.n_cycles, settings.directed, settings.target, settings.seed)
    if settings.kind == "city":
        return es.city_instance(settings.side, settings.nettype, settings.seed)
    raise ValueError(f"unbekannte Instanzart {settings.kind}")


def analyse(settings):
    inst = _instance(settings)
    if inst.directed:
        adj = ea.adjacency_directed(inst.n, inst.edges, settings.order, settings.seed)
        cls = ea.classify_directed(adj)
        hr = ea.hierholzer_directed(adj) if cls == "circuit" else None
        return Analysis(inst.n, inst.m, True, cls, 0, hierholzer=hr)
    adj = ea.adjacency(inst.n, inst.edges, settings.order, settings.seed)
    cls = ea.classify(adj)
    odd = len(ea.odd_nodes(adj))
    hr = fr = None
    ratio = None
    if cls in ("circuit", "path"):
        hr = ea.hierholzer(adj)
        fr = ea.fleury(adj)
        ratio = fr.steps / hr.steps if hr.steps else None
    return Analysis(inst.n, inst.m, False, cls, odd, hr, fr, ratio)


def run_config(settings, seeds=C.SWEEP_SEEDS):
    """Median über feste Seeds derselben Konfiguration (n/n_cycles/target/kind unverändert, nur der Instanz-Seed läuft)."""
    def make(seed):
        s = Settings(**{**settings.__dict__, "seed": seed})
        return analyse(s)

    rows = [make(seed) for seed in seeds]
    return rows


def _median(vals):
    vals = sorted(vals)
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


def cost_sweep(ns, n_cycles=4, target="circuit", seeds=C.SWEEP_SEEDS):
    """Hierholzer- gegen Fleury-Elementarschritte über die Größe (Eulernetz-Instanzen, Median über `seeds`)."""
    out = []
    for n in ns:
        rows = [analyse(Settings("euler", n, n_cycles, target, False, seed=seed)) for seed in seeds]
        h_steps, f_steps, ms = [a.hierholzer.steps for a in rows], [a.fleury.steps for a in rows], [a.m for a in rows]
        out.append({"n": n, "m": _median(ms), "hierholzer": _median(h_steps), "fleury": _median(f_steps), "ratio": _median(f_steps) / _median(h_steps) if _median(h_steps) else None})
    return out


def eulerian_share_sweep(nettype, sides, seeds=C.SWEEP_SEEDS):
    """Anteil der Instanzen (Betriebsnetz/Zufallsgraph), die eulersch sind (Kreis/Weg/keins), über die Rastergröße; Median der Zahl ungerader Knoten bei "keins" als Distanzmaß."""
    out = []
    for side in sides:
        counts = {"circuit": 0, "path": 0, "none": 0}
        odd_when_none = []
        for seed in seeds:
            a = analyse(Settings("city", side=side, nettype=nettype, seed=seed))
            counts[a.classification] += 1
            if a.classification == "none":
                odd_when_none.append(a.odd_count)
        total = len(seeds)
        out.append({
            "side": side,
            "n": side * side,
            "share_circuit": counts["circuit"] / total,
            "share_path": counts["path"] / total,
            "share_none": counts["none"] / total,
            "median_odd_when_none": sorted(odd_when_none)[len(odd_when_none) // 2] if odd_when_none else 0,
        })
    return out
