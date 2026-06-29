import sys
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# VBZ Fahrzeiten SOLL-IST, Jahresarchiv 2022 (URLs stabil, wird nicht mehr nachgefuehrt)
# Woche Mo-So 13.-19.03.2022, keine Feiertage
DATASET = "vbz_fahrzeiten_ogd_2022"
BASE = f"https://data.stadt-zuerich.ch/dataset/{DATASET}/download"

WEEK_FILENAME = "Fahrzeiten_SOLL_IST_20220313_20220319.csv"
WEEK_URL = f"{BASE}/{WEEK_FILENAME}"
HALTESTELLE_URL = f"{BASE}/Haltestelle.csv"
HALTEPUNKT_URL = f"{BASE}/Haltepunkt.csv"


def download(url: str, target: Path) -> None:
    if target.exists():
        size_mb = target.stat().st_size / 1_000_000
        print(f"  [skip] {target.name} ({size_mb:.1f} MB)")
        return

    print(f"  [get ] {target.name}")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = 0
        with open(target, "wb") as f:
            for chunk in r.iter_content(chunk_size=1_000_000):
                f.write(chunk)
                total += len(chunk)
                if total % 10_000_000 < 1_000_000:
                    print(".", end="", flush=True)
        print(f"\n  [done] {total / 1_000_000:.1f} MB")


def main() -> None:
    print(f"Saving to: {DATA_DIR}\n")
    files = [
        (HALTESTELLE_URL, DATA_DIR / "Haltestelle.csv"),
        (HALTEPUNKT_URL, DATA_DIR / "Haltepunkt.csv"),
        (WEEK_URL, DATA_DIR / WEEK_FILENAME),
    ]
    for url, target in files:
        try:
            download(url, target)
        except requests.HTTPError as e:
            print(f"\n  [FAIL] {target.name}: {e}")
            print(f"  URL was: {url}")
            sys.exit(1)
    print("\nAll files ready.")


if __name__ == "__main__":
    main()
