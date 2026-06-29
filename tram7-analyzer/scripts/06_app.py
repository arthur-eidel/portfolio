from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PARQUET = DATA_DIR / "tram7_clean.parquet"

ON_TIME_THRESHOLD_SEC = 120
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.set_page_config(page_title="Tram 7 Pünktlichkeit", page_icon="🚊", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_parquet(PARQUET)


df_full = load_data()

st.title("🚊 Tram 7 Pünktlichkeits-Analyzer")
st.caption(
    f"Data: VBZ SOLL-IST week of March 13–19, 2022 · "
    f"{len(df_full):,} stop events"
)

st.sidebar.header("Filters")
hour_range = st.sidebar.slider("Hour of day", 0, 23, (5, 23), step=1)
selected_weekdays = st.sidebar.multiselect(
    "Weekdays", options=WEEKDAY_NAMES, default=WEEKDAY_NAMES
)
selected_weekday_nums = [WEEKDAY_NAMES.index(d) for d in selected_weekdays]
all_stops = sorted(df_full["stop_name"].dropna().unique())
selected_stops = st.sidebar.multiselect("Stops (empty = all)", options=all_stops, default=[])

df = df_full[
    (df_full["hour"] >= hour_range[0])
    & (df_full["hour"] <= hour_range[1])
    & (df_full["weekday_num"].isin(selected_weekday_nums))
]
if selected_stops:
    df = df[df["stop_name"].isin(selected_stops)]

if len(df) == 0:
    st.warning("No data matches these filters. Loosen them.")
    st.stop()

on_time_pct = (df["delay_sec"].abs() <= ON_TIME_THRESHOLD_SEC).mean() * 100
late_pct = (df["delay_sec"] > ON_TIME_THRESHOLD_SEC).mean() * 100
median_delay = df["delay_sec"].median()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows in view", f"{len(df):,}")
col2.metric("On time (≤2 min)", f"{on_time_pct:.1f}%")
col3.metric("Late (>2 min)", f"{late_pct:.1f}%")
col4.metric("Median delay", f"{median_delay:+.0f} s")

tab1, tab2, tab3 = st.tabs(["Overview", "By Stop", "Heatmap"])

with tab1:
    st.subheader("Median delay by hour of day")
    by_hour = (
        df.groupby("hour")
          .agg(
              n=("delay_sec", "size"),
              median_delay_sec=("delay_sec", "median"),
              mean_delay_sec=("delay_sec", "mean"),
          )
          .reset_index()
    )
    by_hour = by_hour[by_hour["n"] >= 50]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=by_hour["hour"],
        y=by_hour["median_delay_sec"],
        mode="lines+markers",
        name="Median",
        line=dict(color="#0066cc", width=3),
        marker=dict(size=8),
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        xaxis_title="Hour of day",
        yaxis_title="Median delay (seconds)",
        template="plotly_white",
        height=420,
        xaxis=dict(dtick=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("By weekday")
    by_weekday = (
        df.groupby(["weekday_num", "weekday"])
          .agg(
              n=("delay_sec", "size"),
              median_delay_sec=("delay_sec", "median"),
              pct_late=("delay_sec",
                        lambda s: (s > ON_TIME_THRESHOLD_SEC).mean() * 100),
          )
          .reset_index()
          .sort_values("weekday_num")
    )
    fig2 = px.bar(
        by_weekday,
        x="weekday",
        y="median_delay_sec",
        text_auto=".0f",
        labels={"weekday": "", "median_delay_sec": "Median delay (s)"},
        color="median_delay_sec",
        color_continuous_scale=["#22aa44", "#ffffff", "#cc2222"],
        color_continuous_midpoint=0,
    )
    fig2.update_layout(template="plotly_white", height=360, coloraxis_showscale=False)
    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Stops ranked by median delay")
    by_stop = (
        df.groupby("stop_name")
          .agg(
              n=("delay_sec", "size"),
              median_delay_sec=("delay_sec", "median"),
              mean_delay_sec=("delay_sec", "mean"),
              pct_late=("delay_sec",
                        lambda s: (s > ON_TIME_THRESHOLD_SEC).mean() * 100),
          )
          .reset_index()
          .query("n >= 50")
          .sort_values("median_delay_sec")
    )
    fig3 = px.bar(
        by_stop,
        x="median_delay_sec",
        y="stop_name",
        orientation="h",
        color="median_delay_sec",
        color_continuous_scale=["#22aa44", "#ffffff", "#cc2222"],
        color_continuous_midpoint=0,
        hover_data={"n": True, "pct_late": ":.1f"},
    )
    fig3.update_layout(
        xaxis_title="Median delay (seconds)",
        yaxis_title="",
        template="plotly_white",
        height=max(400, 22 * len(by_stop)),
        coloraxis_showscale=False,
    )
    fig3.add_vline(x=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("Raw table"):
        st.dataframe(by_stop.round(2), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Median delay: hour × weekday")
    heatmap = df.pivot_table(
        index="hour", columns="weekday_num", values="delay_sec", aggfunc="median"
    )
    heatmap = heatmap.reindex(columns=sorted(heatmap.columns))
    heatmap.columns = [WEEKDAY_NAMES[i] for i in heatmap.columns]

    fig4 = go.Figure(data=go.Heatmap(
        z=heatmap.values,
        x=heatmap.columns,
        y=heatmap.index,
        colorscale=[
            [0.0, "#22aa44"],
            [0.5, "#ffffff"],
            [1.0, "#cc2222"],
        ],
        zmid=0,
        colorbar=dict(title="Median<br>delay (s)"),
        hovertemplate="%{x} %{y}:00<br>Median: %{z}s<extra></extra>",
    ))
    fig4.update_layout(
        xaxis_title="Weekday",
        yaxis_title="Hour of day",
        yaxis=dict(autorange="reversed", dtick=1),
        template="plotly_white",
        height=600,
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.caption("Built with pandas + plotly + streamlit. Source: Open Data Zürich, VBZ Fahrzeiten SOLL-IST.")
