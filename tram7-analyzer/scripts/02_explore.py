from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WEEK_FILE = DATA_DIR / "Fahrzeiten_SOLL_IST_20220313_20220319.csv"
HALTESTELLE_FILE = DATA_DIR / "Haltestelle.csv"
HALTEPUNKT_FILE = DATA_DIR / "Haltepunkt.csv"


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def explore(name: str, df: pd.DataFrame) -> None:
    section(name)
    print(f"Shape: {df.shape[0]:,} rows  x  {df.shape[1]} columns")
    print(f"Memory: {df.memory_usage(deep=True).sum() / 1_000_000:.1f} MB")
    print("\nColumns and dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"  {col:30s}  {dtype}")
    print("\nFirst 3 rows:")
    print(df.head(3).to_string())


def main() -> None:
    haltestelle = pd.read_csv(HALTESTELLE_FILE)
    explore("Haltestelle.csv (stop names)", haltestelle)

    haltepunkt = pd.read_csv(HALTEPUNKT_FILE)
    explore("Haltepunkt.csv (stop GPS coordinates)", haltepunkt)

    # nur die ersten 100k Zeilen zum Reinschauen, der File ist ~250 MB
    section("Fahrzeiten (peek - first 100,000 rows)")
    peek = pd.read_csv(WEEK_FILE, nrows=100_000)
    explore("Fahrzeiten peek", peek)

    section("Lines in the peek (top 20)")
    print(peek["linie"].value_counts().head(20).to_string())


if __name__ == "__main__":
    main()
