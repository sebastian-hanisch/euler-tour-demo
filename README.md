# Eulertouren – jede Kante genau einmal – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-euler-tour-demo.streamlit.app/)**

Viertes Stück der **Graphen-und-Netzwerke-Reihe** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning", Kind der Brücken-Demo ([bridges-demo](https://github.com/sebastian-hanisch/bridges-demo)). Ein **Eulerkreis** besucht jede Kante eines Netzes genau einmal und kehrt zum Start zurück; ein **Eulerweg** tut dasselbe, ohne zurückzukehren. Ein zusammenhängendes Netz hat genau dann einen Eulerkreis, wenn jeder Knoten geraden Grad hat, und genau dann einen Eulerweg, wenn genau zwei Knoten ungeraden Grad haben – die Zahl der ungeraden Knoten ist nach dem Handschlaglemma immer gerade. Zwei Verfahren finden dieselbe Tour: **Hierholzer** (Teilkreise verschmelzen, O(n + m)) und **Fleury** (schrittweise, meidet eine **Brücke** im noch nicht benutzten Restnetz, außer es bleibt keine Alternative – dafür braucht er bei *jedem* Schritt den Brückentest aus der Brücken-Demo, O(m·(n + m))). Gemessen wird der Aufwandsunterschied und wie selten ein Zufallsnetz überhaupt spontan eulersch ist.

**Einordnung in die Reihe:** die Reihe hat dreizehn Stücke (zwölf im Baum, dazu die Fall-Demo interne-verlinkung-demo), dies ist das vierte (Details in `graphen-planung/PLAN.md` des Portfolio-Ordners):

```
1 BFS und DFS (Wurzel)                                                        [gebaut: bfs-dfs-demo]
 ├─ 2 Brücken und Artikulationspunkte ─ 4 Euler-Touren                        [gebaut: bridges-demo] [DIESES STÜCK]
 ├─ 3 Starke Zusammenhangskomponenten, topologische Sortierung                [gebaut: scc-demo]
 ├─ 5 Graphfärbung                                                            [gebaut: graph-coloring-demo]
 ├─ 6 Zentralität ─ 7 Strukturkennzahlen                                      [gebaut: centrality-demo, strukturkennzahlen-demo]
 │        ├─ 8 Robustheit ─ 9 Kaskaden und Ausbreitung                        [gebaut: robustheit-demo, kaskaden-demo]
 │        └─ 10 Kritische Knoten härten                                       [gebaut: haertung-demo]
 └─ 11 Bandbreite ─ 12 Bandbreite von G(n,k,b) und Cliquenüberdeckung         [gebaut: bandbreite-demo, cliquenbandbreite-demo]
```

Ergebnis in Kürze: **Fleury ist deutlich teurer als Hierholzer, und der Faktor wächst mit der Größe – von etwa dem 6.9-Fachen bei n = 8 auf das 30-Fache bei n = 60 (325 gegen 9830 Elementarschritte).** Ohne gezielte Konstruktion ist Eulerizität selten: ein 2 × 2-Raster (4 Knoten, ein einfacher Kreis) ist immer ein Eulerkreis, aber schon ab 4 × 4 Knoten (16 Knoten) ist praktisch **keine** der 100 gemessenen Instanzen mehr eulersch – weder im Raster noch im Zufallsgraphen gleicher Kantenzahl. Ein einzelner Knoten ganz ohne Kante macht dabei den **ganzen** Graphen nicht eulersch, selbst wenn alle übrigen Grade gerade sind – ein Fallstrick, den networkx' eigene `is_eulerian`-Prüfung bestätigt, nicht nur eine Annahme dieser Demo.

## Warum dieses Problem

Das Königsberger Brückenproblem (Euler, 1736) ist der Geburtsmoment der Graphentheorie: sieben Brücken, die Frage, ob ein Spaziergang jede genau einmal überquert, ist unlösbar – und der Grund ist rein kombinatorisch (Grad der Landmassen), nicht geografisch. Dieselbe Frage ist heute praktisch: eine Räumfahrzeug-Route, ein Leitungstest, ein Zeichenrätsel – wann lässt sich ein Netz "in einem Zug" durchlaufen, ohne eine Verbindung zweimal zu benutzen? Die Demo zeigt die beiden klassischen Antworten (Hierholzer, Fleury) und macht sichtbar, wie viel der Brückentest bei Fleury tatsächlich kostet.

Abgrenzung: die **Arc-Routing-Demo** (Chinesischer Postbote) paart ungerade Knoten, um ein Netz erst eulersch zu **machen** (minimale Verdopplung von Kanten); hier wird vorausgesetzt, dass ein Netz (fast) schon eulersch ist, und die Tour selbst gesucht – keine Überschneidung, nur eine Grenzlinie.

## Vorab-Hypothesen (vor der Messung notiert, hier geprüft)

| Hypothese | Ergebnis |
|---|---|
| **H1** Hierholzer und Fleury finden beide eine gültige Tour, wo eine existiert. | ✅ Bestätigt (Satz, im Test gegen networkx auf über 400 Instanzen: Eulernetz-Kreis/-Weg, Betriebsnetz, Zufallsgraph, Haus vom Nikolaus, gerichteter Fall). |
| **H2** Fleury ist nur wenig teurer als Hierholzer. | ❌ **Widerlegt:** der Faktor wächst deutlich mit der Größe – 6.9-fach bei n = 8, 12.9-fach bei n = 16, 30.2-fach bei n = 60 (Hierholzer 325, Fleury 9830 Elementarschritte). |
| **H3** Isolierte Knoten (ohne Kante) sind für die Eulerkreis-Eigenschaft harmlos, solange die übrigen Knoten gerade Grade haben. | ❌ **Widerlegt – bewusst als Fallstrick geprüft:** ein einzelner Knoten ganz ohne Kante macht den *ganzen* Graphen nicht eulersch, obwohl er nie besucht werden müsste – exakt networkx' `is_eulerian`-Konvention, gegen networkx bestätigt statt angenommen (`test_isolated_node_breaks_an_otherwise_eulerian_graph`). |
| **H4** Zufallsnetze sind selten, aber nicht extrem selten spontan eulersch. | ❌ **Widerlegt – noch seltener als erwartet:** bei sehr kleinen Netzen (2 × 2-Raster, 4 Knoten) ist Eulerizität die Regel (Raster immer, Zufallsgraph zu 100 % Kreis oder Weg), aber schon ab 16 Knoten ist sie in 100 gemessenen Instanzen **kein einziges Mal** aufgetreten – weder im Raster noch im Zufallsgraphen. |
| **H5** Der gerichtete Fall (Eingangsgrad = Ausgangsgrad + Zusammenhang) verhält sich analog zum ungerichteten. | ✅ Bestätigt: die per Konstruktion balancierten, zusammenhängenden gerichteten Eulernetze sind in jedem gemessenen Fall (> 100 Instanzen) ein Eulerkreis, exakt wie networkx' gerichtete `is_eulerian`-Prüfung. |

## Befunde (gemessen, keine Behauptungen)

Median über 5 feste Instanzen (Seeds 100000–100004) für den Aufwand, 100 feste Instanzen je Größe für den Eulerizitäts-Anteil; alle Verfahren sind deterministisch, die Instanzen kommen aus Python-`random` mit festem Seed.

| Frage | Ergebnis |
|---|---|
| **Stimmt das Verfahren?** | ✅ Hierholzer und Fleury (ungerichtet), Hierholzer (gerichtet) und die Klassifikation (Kreis/Weg/keins) stimmen mit networkx (`is_eulerian`, `has_eulerian_path`) auf über 400 Instanzen überein (Eulernetz, Betriebsnetz, Zufallsgraph, Haus vom Nikolaus, gerichtet, n = 1, isolierte Knoten, unzusammenhängend) |
| **Aufwand über die Größe** (Eulerkreis-Netze) | Hierholzer / Fleury: **55/378** (n=8), **88/927** (n=12), **112/1441** (n=16), **154/2821** (n=20), **187/3728** (n=30), **268/7989** (n=40), **325/9830** (n=60) – Faktor **6.9 → 30.2** |
| **Anteil eulersch (Raster)** | Seitenlänge 2: **100 %** (immer Eulerkreis); ab Seitenlänge 4 (16 Knoten): **0 %** |
| **Anteil eulersch (Zufallsgraph, gleiche Kantenzahl)** | Seitenlänge 2: **100 %** (35 % Kreis, 65 % Weg); ab Seitenlänge 4: **0 %** |
| **Gerichteter Eulerkreis** (16 Knoten, 38 Bögen) | Hierholzer (gerichtet) braucht **115** Elementarschritte |

Presets (7), alle mit den Zahlen in ihren Hilfetexten (`tests/test_presets.py`):

| Preset | Was es zeigt |
|---|---|
| Haus vom Nikolaus (Lehrbuch) | 5 Kreuzungen, 8 Straßen: die beiden unteren Ecken (Grad 3) sind ungerade, die übrigen gerade – ein Eulerweg, muss an einer der beiden unteren Ecken beginnen und an der anderen enden |
| Eulerkreis (Standardfall) | 16 Knoten, 29 Kanten (3 kantendisjunkte Kreise): alle Grade gerade; Hierholzer 88, Fleury 807 Elementarschritte (9.2-fach) |
| Eulerweg (ein ungerades Paar) | Dieselbe Konstruktion, eine Kante fehlt (28 Kanten): genau 2 ungerade Knoten; Hierholzer 85, Fleury 718 Elementarschritte |
| Gerichteter Eulerkreis | 16 Knoten, 38 Bögen (gerichtete Kreisvereinigung): Eingangsgrad = Ausgangsgrad überall, zusammenhängend; Hierholzer (gerichtet) 115 Elementarschritte |
| Betriebsnetz (nicht eulersch) | 8 × 8 Kreuzungen (64 Knoten, 112 Straßen): 24 Kreuzungen ungerade (jede Randkreuzung außer den vier Ecken) – weder Kreis noch Weg |
| Zufallsgraph (viele ungerade Knoten) | Dieselbe Knoten-/Kantenzahl, beliebige Paare: 36 ungerade Knoten – noch mehr als im Raster |
| Aufwand: Hierholzer gegen Fleury | Über die Größe gemessen: bei n = 8 das 6.9-Fache, bei n = 60 das 30.2-Fache (325 gegen 9830 Elementarschritte) |

## Modell und Verfahren

- **Instanz** (`eul_scenario.py`): das **Eulernetz** wird aus einem Basiskreis über alle Knoten (garantiert Zusammenhang und keinen isolierten Knoten) plus weiteren zufälligen, **kantendisjunkten** Kreisen konstruiert – jeder Kreis erhöht ungerichtet den Grad, gerichtet Eingangs- und Ausgangsgrad seiner Knoten um je 1, die Vereinigung ist deshalb immer eulersch. Kantendisjunkt ist entscheidend: teilen sich zwei Kreise eine Kante, würde sie im einfachen Graphen nur einmal gezählt und die Gradparität bräche. Für einen Eulerweg wird am Ende eine Kante entfernt (bzw. gerichtet ein neuer Bogen ergänzt), was genau zwei Knoten ungerade macht. Das **Betriebsnetz** (Raster) und der **Zufallsgraph** gleicher Kantenzahl sind gewöhnliche, garantiert zusammenhängende Netze wie in Stück 1–3, ohne Eulerizität zu erzwingen. Das Lehrbuchbeispiel **Haus vom Nikolaus** ist von Hand nachrechenbar.
- **Hierholzer** (`eul_algorithm.hierholzer`): iterativ einem unbenutzten Nachbarn folgen, bis keiner mehr da ist; die entstandene Sackgasse rückwärts abgehen und an jedem Knoten mit noch unbenutzten Kanten einen dort neu gefundenen Teilkreis einfügen. Bei einem Eulerweg **muss** an einem der beiden ungeraden Knoten begonnen werden – sonst bleibt die Suche in einem Teilkreis stecken, der nie zum Start zurückkehrt (ein Fallstrick, der beim Bau tatsächlich auftrat, siehe Tests). Aufwand O(n + m).
- **Fleury** (`eul_algorithm.fleury`): vom aktuellen Knoten aus wird eine Kante gewählt, die im **Restnetz** (nur unbenutzte Kanten) keine Brücke ist, sofern eine Alternative existiert; nur wenn jede verbleibende Kante eine Brücke ist, wird sie überquert. Der Brückentest ist eine **wortgleiche Kopie von `low_link` aus der Brücken-Demo**, hier bei *jedem* Schritt auf dem kompletten Restnetz neu berechnet.
- **Klassifikation** (`classify`, `classify_directed`): ein Eulerkreis existiert genau dann, wenn der **ganze** Graph zusammenhängend ist (auch ein isolierter Knoten muss es sein) und jeder Knoten geraden Grad hat; ein Eulerweg, wenn zusätzlich genau zwei Knoten ungeraden Grad haben. Gerichtet: Eingangsgrad = Ausgangsgrad an jedem Knoten und der zugrunde liegende (ungerichtete) Graph ist zusammenhängend.
- **Elementarschritte:** jeder abgearbeitete Knoten und jede von einem Ende angesehene Kante zählt 1; ein Näherungsmaß, keine Laufzeit.

## Was die App zeigt

1. **Vier Schritte** (Schritt-Regler): **Hierholzer und Fleury in Aktion** (Verfahrenswahl, Regler über die Tour-Schritte, Wiedergabe auf der Karte mit rot markierten Brückenüberquerungen) → **Eulerkreis oder -weg?** (Netz ohne Tour, Gradhistogramm mit ungeraden Knoten rot, Klassifikation) → **Gerichteter Fall** (dieselbe Konstruktion mit gerichteten Bögen, Pfeile, Balance- und Zusammenhangs-Check) → **Aufwand und Zufalls-Sweep** (auf Abruf: Hierholzer gegen Fleury über die Größe; Anteil eulerscher Betriebsnetze/Zufallsgraphen über die Größe).
2. Regler: Instanz (Eulernetz / Betriebsnetz-Zufallsgraph / Haus vom Nikolaus), bei Eulernetz: Knotenzahl, Zahl der Kreise, Ziel (Kreis/Weg); bei Betriebsnetz: Kreuzungen je Seite, Netztyp; Nachbarreihenfolge (fest/gemischt), Zufalls-Seed (+🎲); Permalink in der Adresszeile.

## Was nicht funktioniert hat / Grenzen

- **H2 bis H4 widerlegt.** Fleury ist nicht "nur etwas" teurer, sondern der Faktor wächst deutlich mit der Größe; isolierte Knoten sind kein harmloser Sonderfall; Eulerizität ist bei realistischen Größen praktisch nie spontan gegeben.
- **Fleury nur ungerichtet.** Der gerichtete Fall nutzt ausschließlich Hierholzer; eine gerichtete Entsprechung des Brückentests wurde nicht gebaut.
- **Kein Chinesischer Postbote.** Diese Demo setzt (fast) Eulerizität voraus und sucht die Tour; das Paaren ungerader Knoten, um ein beliebiges Netz erst eulersch zu machen, ist die Arc-Routing-Demo.
- **Konstruierte Eulernetze.** Die Kreisvereinigung ist ein künstliches Konstruktionsverfahren, kein Modell realer Netze; das Betriebsnetz/der Zufallsgraph sind ehrlich fast nie eulersch – das ist der gemessene Punkt, nicht ein Mangel der Instanzen.
- **Elementarschritte statt Laufzeit.** Der Faktor (bis 30-fach) gilt für das Zählmaß, echte Laufzeiten hängen an der Implementierung.
- **Einfache Graphen.** Keine Mehrfachkanten, keine Schleifen.

## Tests

`tests/test_algorithm.py` (Hierholzer/Fleury ungerichtet und gerichtet gegen networkx auf über 400 Instanzen, Klassifikations-Fallstricke "gerade Grade aber unzusammenhängend" und "isolierter Knoten", Handschlaglemma, Haus vom Nikolaus von Hand, Fleury-Brücken-Invariante, Buchführung, Sonderfälle), `tests/test_scenario.py`, `tests/test_evaluation.py`, `tests/test_presets.py` (jede Zahl der Hilfetexte), `tests/test_claims.py` (jede README-Zahl über die echten Auswertungsfunktionen), `tests/test_app.py` (40: AppTest – Voreinstellung, jedes Preset, jeder Schritt für jede Instanz, jedes Ziel und beide Netztypen, jede Position des Tour-Schritt-Reglers, Randwerte, Permalink-Grenzen, bedingte Regler, Berechnungen auf Abruf, Footer). 85 Tests insgesamt.

```
python -m pytest tests/ -v
```

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-App |
| `eul_algorithm.py` | Hierholzer (ungerichtet/gerichtet), Fleury, Low-Link-Kopie, Klassifikation |
| `eul_scenario.py` | Eulernetz, Betriebsnetz/Zufallsgraph, Haus vom Nikolaus |
| `eul_evaluation.py` | Analyse, Sweeps (Aufwand, Eulerizitäts-Anteil) |
| `eul_visualization.py` | Plotly-Figuren (Tour-Wiedergabe, Gradhistogramm, gerichteter Fall mit Pfeilen) |
| `eul_presets.py`, `eul_constants.py` | Permalink, Presets, gemessene Werte |
| `tests/` | Tests |

## Bewusst nicht umgesetzt

Graphfärbung, Zentralität, Robustheit und Kaskaden, kritische Knoten härten, Bandbreite – eigene Stücke der Reihe. Gerichtetes Fleury, Chinesischer Postbote (Arc-Routing-Demo).

## Lokal ausführen

```
python -m venv venv
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\streamlit run app.py
```

## Literatur

- Euler, L. (1741). *Solutio problematis ad geometriam situs pertinentis.* Commentarii Academiae Scientiarum Imperialis Petropolitanae 8, 128–140.
- Hierholzer, C., & Wiener, C. (1873). *Ueber die Möglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren.* Mathematische Annalen 6(1), 30–32 (Hierholzer war zum Zeitpunkt der Veröffentlichung bereits verstorben; Wiener gab die Arbeit posthum heraus).
- Fleury, M. (1883). *Deux problèmes de géométrie de situation.* Journal de mathématiques élémentaires, 2e série, 2, 257–261.

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html).
