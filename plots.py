import data
import folium as f
from folium.plugins import FastMarkerCluster
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


def heatmap():
    st.markdown('# 🗺️ USA Unfall-Heatmap')

    df =  data.load_data()

    MAX_POINTS = 50000
    df_good = df.loc[~df["Start_Lat"].isna(), ["Start_Lat", "Start_Lng"]]

    if len(df_good.index) > MAX_POINTS:
        df_good = df_good.sample(MAX_POINTS, random_state=42)


    m = f.Map(location=[df['Start_Lat'].mean(), df['Start_Lng'].mean()], zoom_start=7)

    coordinates = df_good.values.tolist()

    FastMarkerCluster(coordinates).add_to(m)

    st_data = st_folium(m, width=725)


def hour_of_day(df):

    # ---------- Daten vorbereiten ----------
    df = df.copy()
    df['Start_Time'] = pd.to_datetime(df['Start_Time'], format='mixed')
    df = df[['Start_Time', 'Severity']].dropna()
    df['Hour'] = df['Start_Time'].dt.hour

    hours = range(24)

    # ---------- Alle Unfälle ----------
    hour_all = (
        df.groupby('Hour')
          .size()
          .reindex(hours, fill_value=0)
    )

    # ---------- Schwere Unfälle ----------
    df_severe = df[df['Severity'] >= 3]

    hour_severe = (
        df_severe.groupby('Hour')
                 .size()
                 .reindex(hours, fill_value=0)
    )

    ymax = max(hour_all.max(), hour_severe.max()) * 1.1

    # ---------- Plot ----------
    st.subheader("Unfälle nach Uhrzeit")

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    axes[0].bar(hour_all.index, hour_all.values)
    axes[0].set_title("Alle Unfälle")
    axes[0].set_ylabel("Anzahl")
    axes[0].set_ylim(0, ymax)

    axes[1].bar(hour_severe.index, hour_severe.values)
    axes[1].set_title("Schwere Unfälle (Severity ≥ 3)")
    axes[1].set_ylabel("Anzahl")
    axes[1].set_xlabel("Hour of Day (0 = Mitternacht)")
    axes[1].set_ylim(0, ymax)

    plt.tight_layout()
    st.pyplot(fig)

    # ---------- Insight berechnen ----------
    night_hours = list(range(22, 24)) + list(range(0, 6))
    day_hours = list(range(6, 22))

    night_share = (
        hour_severe[night_hours].sum() /
        hour_all[night_hours].sum()
        if hour_all[night_hours].sum() > 0 else 0
    )

    day_share = (
        hour_severe[day_hours].sum() /
        hour_all[day_hours].sum()
        if hour_all[day_hours].sum() > 0 else 0
    )

    # ---------- Insight anzeigen ----------
    st.markdown(
    f"### Insight: \nEntgegen der Erwartung ist der Anteil schwerer Unfälle tagsüber höher ({day_share:.1%}) als nachts ({night_share:.1%})."
    "Ein möglicher Grund ist das deutlich höhere Verkehrsaufkommen am Tag."
    )

   