from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
IN_FILE = DATA_DIR / "tram7_clean.parquet"
OUT_DIR = DATA_DIR / "analysis"
OUT_DIR.mkdir(exist_ok=True)

# VBZ zaehlt eine Abfahrt innerhalb 2 min als puenktlich -> gleiche Grenze nehmen
ON_TIME_THRESHOLD_SEC = 120


def section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main() -> None:
    df = pd.read_parquet(IN_FILE)
    print(f"Loaded {len(df):,} Tram 7 rows from {IN_FILE.name}")

    section("Headline: how punctual is Tram 7?")
    on_time = (df["delay_sec"].abs() <= ON_TIME_THRESHOLD_SEC).mean()
    early = (df["delay_sec"] < -ON_TIME_THRESHOLD_SEC).mean()
    late = (df["delay_sec"] > ON_TIME_THRESHOLD_SEC).mean()
    print(f"  On time  (within 2 min):  {on_time*100:5.1f}%")
    print(f"  Early   (>2 min early):   {early*100:5.1f}%")
    print(f"  Late    (>2 min late):    {late*100:5.1f}%")
    print(f"  Median delay:  {df['delay_sec'].median():+.0f} sec")
    print(f"  Mean delay:    {df['delay_sec'].mean():+.1f} sec")

    section("Delay by hour of day")
    by_hour = (
        df.groupby("hour")
          .agg(
              n=("delay_sec", "size"),
              median_delay_sec=("delay_sec", "median"),
              mean_delay_sec=("delay_sec", "mean"),
              pct_late=("delay_sec", lambda s: (s > ON_TIME_THRESHOLD_SEC).mean() * 100),
          )
          .round(2)
    )
    by_hour = by_hour[by_hour["n"] >= 100]
    print(by_hour.to_string())
    by_hour.to_csv(OUT_DIR / "by_hour.csv")

    section("Delay by weekday")
    by_weekday = (
        df.groupby(["weekday_num", "weekday"])
          .agg(
              n=("delay_sec", "size"),
              median_delay_sec=("delay_sec", "median"),
              pct_late=("delay_sec", lambda s: (s > ON_TIME_THRESHOLD_SEC).mean() * 100),
          )
          .round(2)
          .reset_index()
          .sort_values("weekday_num")
    )
    print(by_weekday.to_string(index=False))
    by_weekday.to_csv(OUT_DIR / "by_weekday.csv", index=False)

    section("Delay by stop (worst 10 by median delay)")
    by_stop = (
        df.groupby("stop_name")
          .agg(
              n=("delay_sec", "size"),
              median_delay_sec=("delay_sec", "median"),
              mean_delay_sec=("delay_sec", "mean"),
              pct_late=("delay_sec", lambda s: (s > ON_TIME_THRESHOLD_SEC).mean() * 100),
          )
          .round(2)
          .query("n >= 100")
          .sort_values("median_delay_sec", ascending=False)
    )
    print(by_stop.head(10).to_string())
    print("\nBEST 10 stops (most on-time):")
    print(by_stop.tail(10).to_string())
    by_stop.to_csv(OUT_DIR / "by_stop.csv")

    section("Heatmap data: median delay by hour x weekday")
    heatmap = (
        df.pivot_table(
            index="hour",
            columns="weekday_num",
            values="delay_sec",
            aggfunc="median",
        )
        .round(1)
    )
    heatmap = heatmap.loc[heatmap.index.isin(range(5, 25))]
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heatmap.columns = [weekday_names[i] for i in heatmap.columns]
    print(heatmap.to_string())
    heatmap.to_csv(OUT_DIR / "heatmap_hour_weekday.csv")

    section("Done")
    print(f"Saved 4 analysis CSVs to {OUT_DIR}")


if __name__ == "__main__":
    main()
