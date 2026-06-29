from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
df = pd.read_parquet(DATA_DIR / "tram7_clean.parquet")

# Reihenfolge der Halte je Richtung aus den Daten selbst rekonstruieren
for direction in sorted(df["richtung"].unique()):
    sub = df[df["richtung"] == direction]
    order = sub.groupby("stop_name")["seq_von"].median().sort_values()
    print(f"\n=== Direction {direction} ({len(sub):,} rows) ===")
    for i, (name, seq) in enumerate(order.items(), start=1):
        print(f"  {i:>2}. seq={seq:>4.0f}  {name}")
