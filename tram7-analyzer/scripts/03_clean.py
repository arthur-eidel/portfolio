from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WEEK_FILE = DATA_DIR / "Fahrzeiten_SOLL_IST_20220313_20220319.csv"
HALTESTELLE_FILE = DATA_DIR / "Haltestelle.csv"
OUT_FILE = DATA_DIR / "tram7_clean.parquet"

USECOLS = [
    "linie",
    "richtung",
    "betriebsdatum",
    "fahrzeug",
    "soll_an_von",
    "ist_an_von",
    "soll_ab_von",
    "ist_ab_von",
    "halt_id_von",
    "fahrt_id",
    "seq_von",
]


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    # chunked lesen, damit der 250-MB-File nie ganz im Speicher liegt
    section("Loading full CSV in chunks (only keeping Linie 7)")

    chunks = []
    chunk_size = 500_000
    total_rows_read = 0
    rows_kept = 0

    reader = pd.read_csv(WEEK_FILE, usecols=USECOLS, chunksize=chunk_size)
    for i, chunk in enumerate(reader):
        total_rows_read += len(chunk)
        tram7 = chunk[chunk["linie"] == 7]
        rows_kept += len(tram7)
        chunks.append(tram7)
        print(f"  chunk {i+1}: read {len(chunk):>7,} rows, "
              f"kept {len(tram7):>5,} Tram 7 rows")

    df = pd.concat(chunks, ignore_index=True)
    print(f"\nTotal rows in CSV: {total_rows_read:,}")
    print(f"Tram 7 rows kept:  {rows_kept:,}  "
          f"({100*rows_kept/total_rows_read:.1f}%)")

    section("Parsing dates")
    # betriebsdatum ist "16.03.22" -> 2-stelliges Jahr
    df["betriebsdatum"] = pd.to_datetime(df["betriebsdatum"], format="%d.%m.%y")
    df["weekday"] = df["betriebsdatum"].dt.day_name()
    df["weekday_num"] = df["betriebsdatum"].dt.dayofweek
    print(df[["betriebsdatum", "weekday", "weekday_num"]].head().to_string())

    section("Computing delays")
    # + = zu spaet abgefahren, - = zu frueh
    df["delay_sec"] = df["ist_ab_von"] - df["soll_ab_von"]
    df["delay_min"] = df["delay_sec"] / 60.0
    df["hour"] = df["soll_ab_von"] // 3600
    print("Delay summary (seconds):")
    print(df["delay_sec"].describe().to_string())

    section("Filtering outliers")
    before = len(df)
    # alles jenseits ~-5 / +30 min ist GPS-Muell oder abgebrochene Fahrten
    df = df[(df["delay_sec"] > -300) & (df["delay_sec"] < 1800)]
    after = len(df)
    print(f"Removed {before-after:,} outlier rows "
          f"({100*(before-after)/before:.2f}%)")
    print(f"Kept {after:,} rows.")

    section("Joining stop names")
    stops = pd.read_csv(HALTESTELLE_FILE, usecols=["halt_id", "halt_lang"])
    df = df.merge(stops, left_on="halt_id_von", right_on="halt_id", how="left")
    df = df.drop(columns=["halt_id"])
    df = df.rename(columns={"halt_lang": "stop_name"})
    print(f"Distinct stops on Tram 7: {df['stop_name'].nunique()}")
    print("\nTop 10 stops by row count:")
    print(df["stop_name"].value_counts().head(10).to_string())

    section("Saving cleaned data")
    df.to_parquet(OUT_FILE, index=False)
    size_mb = OUT_FILE.stat().st_size / 1_000_000
    print(f"Saved {len(df):,} rows to {OUT_FILE.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
