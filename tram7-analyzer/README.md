# Tram 7 Pünktlichkeits-Analyzer

*(English version: [README.en.md](README.en.md))*

Wie pünktlich ist das 7er-Tram in Zürich? Ich hab mir die offenen VBZ-Daten
(Fahrzeiten SOLL-IST-Vergleich von Open Data Zürich) genommen und das mal
durchgerechnet. Der Rohdatensatz für eine Woche sind ~1.4 Mio Zeilen, nach dem
Filtern auf Linie 7 bleiben etwa 58'000 Halte-Events übrig.

Datengrundlage ist die Woche 13.–19.03.2022 (normale Woche, keine Feiertage).
Jede Zeile ist ein Halt eines Fahrzeugs mit Soll- und Ist-Zeit, daraus rechne
ich die Verspätung in Sekunden.

## Was rauskommt

Tram 7 ist ziemlich pünktlich, ~95.6 % innerhalb von ±2 min, Median praktisch 0.
Spannender ist das Muster: Die Verspätung baut sich entlang der Strecke auf und
wird an den Endhaltestellen durch die eingeplante Wendezeit wieder
zurückgesetzt. In der Innenstadt (Paradeplatz, Rennweg) fährt das Tram im
Schnitt sogar leicht zu früh.

## Aufbau

Das Projekt läuft in Stufen, jedes Skript ist ein Schritt:

```
scripts/01_download.py    Daten von Open Data Zürich ziehen (~250 MB)
scripts/02_explore.py     kurz reinschauen: Spalten, Typen, Linien
scripts/03_clean.py       auf Linie 7 filtern, Verspätung rechnen, parquet schreiben
scripts/04_analyze.py     Kennzahlen + CSVs (nach Stunde, Wochentag, Halt)
scripts/05_visualize.py   Plotly-Charts als HTML
scripts/06_app.py         Streamlit-Dashboard
scripts/check_route.py    Halte-Reihenfolge je Richtung aus den Daten
```

## Setup

```
pip install -r requirements.txt
```

## Ablauf

```
python scripts/01_download.py
python scripts/02_explore.py
python scripts/03_clean.py
python scripts/04_analyze.py
python scripts/05_visualize.py
streamlit run scripts/06_app.py
```

Die Skripte 01–04 schreiben ihre Zwischenresultate nach `data/`, die Charts
landen in `charts/`. Das Dashboard öffnet sich im Browser unter `localhost:8501`.

## Stack

Python, pandas, Plotly, Streamlit. Daten: Open Data Zürich (VBZ Fahrzeiten
SOLL-IST-Vergleich), Lizenz CC0.
