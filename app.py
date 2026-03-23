import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as graph_objects
from datetime import datetime

# Page layout
st.set_page_config(page_title = "L22 Weather API Dashboard", layout = "wide")

st.sidebar.header("Settings")
city = st.sidebar.text_input("City Name:", "Lakeland")
unit = st.sidebar.selectbox("Measurement:", ["Celsius", 
"Farenheit"])
api_key = st.secrets["OPENWEATHER_API_KEY"]
unit_param = "metric" if "Celsius" in unit else "imperial"

# API fetching
@st.cache_data
def fetch_weather(city_name, api_key, units = "imperial"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units={units}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data
def fetch_forecast(city_name, api_key, units = "imperial"):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units={units}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df pd.DataFrame(data['list'])
        df['datetime'] = pd.to_datetime(df['dt_txt'])
        df['temp'] = df['main'].apply(lambda x: x['temp'])
        df['humidity'] = df['main'].apply(lambda x: x['humidity'])
        df['weather'] = df['weather'].apply(lambda x: x[0]['main'])
        return df
    return pd.DataFrame()

@st.cache_data
def fetch_air_quality(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        components = data['list'][0]['components']
        df = pd.DataFrame([components])
        df['aqi'] = data['list'][0]['main']['aqi']
        return df
    return pd.DataFrame()

# data fetching
if api_key:
    weather_data = fetch_weather(city, api_key, unit_param)
    if weather_data:
        forecast_df = fetch_forecast(city, api_key, unit_param)
        air_quality_df = fetch_air_quality(weather_data['coord']['lat'], weather_data['coord']['lon'], api_key)
    else:
        st.error("City or API key not found")
        st.stop()

st.title(f"Weather Dashboard for {city}")

# time series chart
st.subheader("5-day Temperature Forecast")
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast_df['datetime'], y=forecast_df['temp'], mode='lines+markers', name='Temperature'))
fig.update_layout(xaxis_title='Date and Time', yaxis_title=f'Temperature ({unit[0:1]})', template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# humidity bar chart
st.subheader("Forecasted Humidity")
st.bar_chart(fig, use_container_width=True)

# forecast data table
st.subheader("Forecast Data Table")
st.dataframe(forecast_df[['datetime', 'temp', 'humidity', 'weather']].sort_values('datetime'))