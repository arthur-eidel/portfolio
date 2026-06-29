# Tram 7 Punctuality Analyzer

*(Deutsche Version: [README.md](README.md))*

How punctual is Zurich's tram line 7? I took the open VBZ data (Fahrzeiten
SOLL-IST-Vergleich from Open Data Zürich) and worked it out. The raw dataset for
one week is ~1.4M rows; after filtering down to line 7, about 58,000 stop events
remain.

The data covers the week of 13–19 March 2022 (a normal week, no public
holidays). Each row is one stop of one vehicle with a scheduled and an actual
time, and I compute the delay in seconds from that.

## What it shows

Tram 7 is pretty punctual: ~95.6% within ±2 min, median essentially 0. The more
interesting bit is the pattern: delay builds up along the route and gets reset at
the termini thanks to the scheduled turnaround time. At central stops
(Paradeplatz, Rennweg) the tram actually runs slightly early on average.

## Layout

The project runs in stages, one script per step:

```
scripts/01_download.py    pull the data from Open Data Zürich (~250 MB)
scripts/02_explore.py     quick look: columns, types, lines
scripts/03_clean.py       filter to line 7, compute delays, write parquet
scripts/04_analyze.py     metrics + CSVs (by hour, weekday, stop)
scripts/05_visualize.py   Plotly charts as HTML
scripts/06_app.py         Streamlit dashboard
scripts/check_route.py    reconstruct stop order per direction from the data
```

## Setup

```
pip install -r requirements.txt
```

## Running it

```
python scripts/01_download.py
python scripts/02_explore.py
python scripts/03_clean.py
python scripts/04_analyze.py
python scripts/05_visualize.py
streamlit run scripts/06_app.py
```

Scripts 01–04 write their intermediate results to `data/`, the charts go to
`charts/`. The dashboard opens in the browser at `localhost:8501`.

## Stack

Python, pandas, Plotly, Streamlit. Data: Open Data Zürich (VBZ Fahrzeiten
SOLL-IST-Vergleich), licensed CC0.
