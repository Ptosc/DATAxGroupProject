import streamlit as st
import plotly.express as px
from plots import hour_of_day
from data import load_data

df = load_data()

st.header('US-Unfälle Datenanalyse')



tab1, tab2, tab3 = st.tabs([
    "Übersicht",
    "Wetter",
    "Timing"
])

with tab1:
    st.write(df.head())
    total_entries = df.shape[0]
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("Total Entries:", total_entries)
    with col2:
        avg_severity = df['Severity'].mean()
        st.write("Average Severity:", round(avg_severity, 2))

with tab2:
    weather_counts = (
        df["Weather_Condition"]
        .value_counts()
        .reset_index()
    )

    weather_counts.columns = ["Weather", "Count"]

    MIN_COUNT = 5000

    mask = weather_counts["Count"] < MIN_COUNT
    other_sum = weather_counts.loc[mask, "Count"].sum()

    weather_counts = weather_counts.loc[~mask]

    if other_sum > 0:
        weather_counts.loc[len(weather_counts)] = ["Other", other_sum]

    fig = px.pie(
        weather_counts,
        names="Weather",
        values="Count",
        title="Weather Conditions – Percentage Share",
        hole=0.5  # Donut-Chart (optional)
    )

    fig.update_traces(
        textinfo="percent+label",
        textposition="inside"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    hour_of_day(df)