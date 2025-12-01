import streamlit as st
import pandas as pd
import requests
from datetime import date
import google.generativeai as genai
import os

st.title("Gemini Chatbot")
st.write("This page integrates Google Gemini to create a chatbot that specializes in answering questions based on the API's domain.")




st.set_page_config(page_title="AI Weather Chatbot", page_icon="💬", layout="wide")

st.title("💬 AI Weather Chatbot")
st.caption("Ask about weather conditions and activity feasibility using real-time data + Google Gemini.")


with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")
    forecast_date = st.date_input("Forecast Date", value=date.today())
    units = st.radio("Units", ["Metric (°C, m/s)", "Imperial (°F, mph)"], index=1)


if forecast_date < date.today():
    st.warning("Please select today or a future date for forecast.")
    st.stop()


geo_url = "https://geocoding-api.open-meteo.com/v1/search"
try:
    r = requests.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"})
    r.raise_for_status()
    if r.json().get("results") is None:
        st.error("Could not find that location. Try another city.")
        st.stop()
except Exception as e:
    st.error(f"Error fetching location: {e}")
    st.stop()

loc = r.json()["results"][0]
lat, lon = loc["latitude"], loc["longitude"]
resolved_name = f'{loc["name"]}, {loc.get("admin1","")}, {loc.get("country","")}'


temp_unit = "fahrenheit" if "Imperial" in units else "celsius"
wind_unit = "mph" if "Imperial" in units else "ms"

weather_url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["temperature_2m", "wind_speed_10m", "precipitation"],
    "start_date": forecast_date.isoformat(),
    "end_date": forecast_date.isoformat(),
    "temperature_unit": temp_unit,
    "wind_speed_unit": wind_unit,
    "timezone": "auto",
}
try:
    wr = requests.get(weather_url, params=params)
    wr.raise_for_status()
    data = wr.json()
except Exception as e:
    st.error(f"Error fetching weather data: {e}")
    st.stop()

hourly = data["hourly"]
df = pd.DataFrame({
    "time": pd.to_datetime(hourly["time"]),
    "temperature": hourly["temperature_2m"],
    "wind_speed": hourly["wind_speed_10m"],
    "precipitation": hourly["precipitation"],
}).set_index("time")


high_temp = df["temperature"].max()
low_temp = df["temperature"].min()
avg_wind = df["wind_speed"].mean()
total_precip = df["precipitation"].sum()


st.subheader("Forecast Summary")
st.write(f"**Location:** {resolved_name}")
st.write(f"**Date:** {forecast_date}")
st.write(f"High: {high_temp:.1f}, Low: {low_temp:.1f}, Avg Wind: {avg_wind:.1f}, Total Precip: {total_precip:.1f}")


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  
model = genai.GenerativeModel("gemini-pro")


st.subheader("Chat with AI about your plans")
st.write("Example: *Is it a good day for hiking? Should I bring an umbrella?*")


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Your question:")
if st.button("Ask"):
    if user_input.strip() == "":
        st.warning("Please enter a question.")
    else:
        
        context = f"""
        Weather data for {resolved_name} on {forecast_date}:
        - High Temp: {high_temp:.1f} {'°F' if 'Imperial' in units else '°C'}
        - Low Temp: {low_temp:.1f} {'°F' if 'Imperial' in units else '°C'}
        - Avg Wind: {avg_wind:.1f} {'mph' if 'Imperial' in units else 'm/s'}
        - Total Precipitation: {total_precip:.1f} mm
        User question: {user_input}
        Answer conversationally and help the user decide if their activity is feasible.
        """

        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(context)
                answer = response.text
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", answer))
        except Exception as e:
            st.error(f"Error generating response: {e}")


for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")

