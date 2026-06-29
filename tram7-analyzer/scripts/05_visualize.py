from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ANALYSIS_DIR = DATA_DIR / "analysis"
CHARTS_DIR = DATA_DIR.parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)


def chart_1_by_hour() -> None:
    df = pd.read_csv(ANALYSIS_DIR / "by_hour.csv")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["hour"],
        y=df["median_delay_sec"],
        mode="lines+markers",
        name="Median delay (sec)",
        line=dict(color="#0066cc", width=3),
        marker=dict(size=8),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray",
                  annotation_text="On schedule")
    fig.add_vrect(x0=7, x1=9, fillcolor="orange", opacity=0.1,
                  line_width=0, annotation_text="AM rush",
                  annotation_position="top left")
    fig.add_vrect(x0=16, x1=19, fillcolor="orange", opacity=0.1,
                  line_width=0, annotation_text="PM rush",
                  annotation_position="top left")
    fig.update_layout(
        title="Tram 7: Median delay by hour of day (March 13-19, 2022)",
        xaxis_title="Hour of day",
        yaxis_title="Median delay (seconds, positive = late)",
        xaxis=dict(dtick=1),
        template="plotly_white",
        height=500,
    )
    out = CHARTS_DIR / "1_by_hour.html"
    fig.write_html(out)
    print(f"  saved {out.name}")


def chart_2_by_stop() -> None:
    df = pd.read_csv(ANALYSIS_DIR / "by_stop.csv")
    df = df.sort_values("median_delay_sec")

    fig = px.bar(
        df,
        x="median_delay_sec",
        y="stop_name",
        orientation="h",
        color="median_delay_sec",
        color_continuous_scale=["#22aa44", "#ffffff", "#cc2222"],
        color_continuous_midpoint=0,
        hover_data={"n": True, "pct_late": ":.1f"},
    )
    fig.update_layout(
        title="Tram 7: Median delay by stop",
        xaxis_title="Median delay (seconds)",
        yaxis_title="",
        template="plotly_white",
        height=800,
        coloraxis_showscale=False,
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    out = CHARTS_DIR / "2_by_stop.html"
    fig.write_html(out)
    print(f"  saved {out.name}")


def chart_3_heatmap() -> None:
    df = pd.read_csv(ANALYSIS_DIR / "heatmap_hour_weekday.csv", index_col=0)
    df = df.loc[df.index <= 23]

    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=[
            [0.0, "#22aa44"],
            [0.5, "#ffffff"],
            [1.0, "#cc2222"],
        ],
        zmid=0,
        colorbar=dict(title="Median<br>delay (s)"),
        hovertemplate="%{x} %{y}:00<br>Median delay: %{z}s<extra></extra>",
    ))
    fig.update_layout(
        title="Tram 7: Median delay by hour x weekday",
        xaxis_title="Weekday",
        yaxis_title="Hour of day",
        yaxis=dict(autorange="reversed", dtick=1),
        template="plotly_white",
        height=700,
    )
    out = CHARTS_DIR / "3_heatmap.html"
    fig.write_html(out)
    print(f"  saved {out.name}")


def main() -> None:
    print(f"Writing charts to {CHARTS_DIR}\n")
    chart_1_by_hour()
    chart_2_by_stop()
    chart_3_heatmap()
    print("\nDone. Open the HTML files in your browser:")
    for f in sorted(CHARTS_DIR.glob("*.html")):
        print(f"  {f}")


if __name__ == "__main__":
    main()
