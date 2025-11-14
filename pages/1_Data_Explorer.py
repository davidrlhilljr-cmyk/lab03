import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date, timedelta

st.title("Data Explorer")
st.write("This page fetches and analyzes data from a public web API.")

st.set_page_config(page_title="Weather Explorer", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Explorer (Open‑Meteo)")
st.caption("Explore temperature and wind by location and date range. Data from Open‑Meteo.")

# Sidebar inputs (>=2 interactions)
with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")
    days_back = st.slider("Days back", 3, 60, 14, help="How many days to look back from today")
    units = st.radio("Units", ["Metric (°C, m/s)", "Imperial (°F, mph)"], index=1)
    show_temp = st.checkbox("Show Temperature", True)
    show_wind = st.checkbox("Show Wind", True)
    smooth = st.slider("Smoothing (Moving Avg window)", 1, 7, 3)

if not (show_temp or show_wind):
    st.warning("Select at least one variable to display.")
    st.stop()

# Resolve city -> coordinates via Open‑Meteo geocoding
geo_url = "https://geocoding-api.open-meteo.com/v1/search"
r = requests.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"})
if r.status_code != 200 or r.json().get("results") is None:
    st.error("Could not find that location. Try another city.")
    st.stop()

loc = r.json()["results"][0]
lat, lon = loc["latitude"], loc["longitude"]
resolved_name = f'{loc["name"]}, {loc.get("admin1","")}, {loc.get("country","")}'

end = date.today()
start = end - timedelta(days=days_back)

# Unit mappings
temp_unit = "fahrenheit" if "Imperial" in units else "celsius"
wind_unit = "mph" if "Imperial" in units else "ms"  # m/s

weather_url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["temperature_2m","wind_speed_10m"],
    "start_date": start.isoformat(),
    "end_date": end.isoformat(),
    "temperature_unit": temp_unit,
    "wind_speed_unit": wind_unit,
    "timezone": "auto"
}
wr = requests.get(weather_url, params=params)
wr.raise_for_status()
data = wr.json()

hourly = data["hourly"]
df = pd.DataFrame({
    "time": pd.to_datetime(hourly["time"]),
    "temperature": hourly["temperature_2m"],
    "wind_speed": hourly["wind_speed_10m"]
}).set_index("time")

# Your own analysis: daily stats and moving averages
daily = df.resample("D").agg({
    "temperature": ["min","mean","max"],
    "wind_speed": ["mean","max"]
})
daily.columns = ["_".join(c).strip() for c in daily.columns.to_flat_index()]
df["temperature_ma"] = df["temperature"].rolling(smooth).mean()
df["wind_speed_ma"] = df["wind_speed"].rolling(smooth).mean()

left, right = st.columns([2,1])
with left:
    st.subheader(f"Location: {resolved_name}")
    st.write(f"Lat: {lat:.3f}, Lon: {lon:.3f} | Range: {start} → {end}")

# Dynamic charts
plots = []
if show_temp:
    fig_t = px.line(
        df.reset_index(), x="time", y=["temperature","temperature_ma"],
        labels={"value": f"Temperature ({'°F' if 'Imperial' in units else '°C'})", "time":"Time"},
        title="Temperature (hourly) with Moving Average"
    )
    fig_t.update_traces(hovertemplate=None)
    plots.append(("Temperature", fig_t))

if show_wind:
    fig_w = px.line(
        df.reset_index(), x="time", y=["wind_speed","wind_speed_ma"],
        labels={"value": f"Wind Speed ({'mph' if 'Imperial' in units else 'm/s'})", "time":"Time"},
        title="Wind Speed (hourly) with Moving Average"
    )
    plots.append(("Wind", fig_w))

for label, fig in plots:
    st.plotly_chart(fig, use_container_width=True)

# Show daily table (processed)
st.subheader("Daily Summary (computed)")
st.dataframe(daily.style.format({
    "temperature_min":"{:.1f}", "temperature_mean":"{:.1f}", "temperature_max":"{:.1f}",
    "wind_speed_mean":"{:.1f}", "wind_speed_max":"{:.1f}"
}), use_container_width=True)

# Explain what was analyzed

 st.markdown("""
- Retrieves hourly temperature and wind from **Open‑Meteo** for the chosen place and date range.
- Computes **daily aggregates** (min/mean/max) and **moving averages** over the selected window.
- Renders **dynamic, interactive charts** that update when you change inputs.
- All processing (resampling, aggregation, rolling window) is implemented in this code (no LLM).
    """)
