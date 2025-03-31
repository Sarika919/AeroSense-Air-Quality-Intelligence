
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from geopy.geocoders import Nominatim

# ------------------ Load Trained Model ------------------
model = joblib.load('aqi_model.pkl')

# ------------------ Streamlit Page Configuration ------------------
st.set_page_config(page_title="Advanced AQI Prediction", layout="wide")

# ------------------ Navbar ------------------
st.markdown(
    """
    <style>
        .navbar {
            background: linear-gradient(to right, #4f46e5, #a855f7);
            overflow: hidden;
            padding: 10px 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .navbar a {
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 12px 20px;
            text-decoration: none;
            transition: background-color 0.3s;
        }
        .navbar a:hover {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
        }
    </style>
    <div class="navbar">
        <a href="#home">🌫️ AQI App</a>
        <a href="#about">ℹ️ About</a>
        <a href="#aqi-prediction">📊 AQI Prediction</a>
        <a href="#real-time">📡 Real-Time AQI</a>
        <a href="#trends">📈 AQI Trends</a>
        <a href="#hourly-trends">🕒 Hourly Trends</a>
        <a href="#maps">🗺️ AQI Maps</a>
        <a href="#forecast">🔮 Forecast AQI</a>
        <a href="#geolocation">📍 Geolocation AQI</a>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ Geolocation to Fetch Correct Location ------------------
def get_location():
    geolocator = Nominatim(user_agent="aqi_app")
    location = geolocator.geocode("Chandigarh, India")
    if location:
        return location.latitude, location.longitude, location.address
    else:
        return None, None, "Location not found"

lat, lon, location_name = get_location()

# ------------------ Chandigarh AQI Data ------------------
chandigarh_aqi_data = pd.DataFrame({
    'location': ['Sector 17', 'Sector 22', 'Sector 35', 'Manimajra', 'ISBT 43', 'Industrial Area', 'Sector 8', 'Sector 10'],
    'lat': [30.7352, 30.7280, 30.7160, 30.7190, 30.7056, 30.7053, 30.7534, 30.7611],
    'lon': [76.7725, 76.7794, 76.7415, 76.8361, 76.8000, 76.8019, 76.7851, 76.7736],
    'aqi': [180, 150, 135, 190, 160, 200, 120, 130]
})

# ------------------ About Section ------------------
if st.button("ℹ️ About AQI"):
    st.markdown(
        """
        ## 🌿 What is AQI?
        The Air Quality Index (AQI) is used to measure and report air quality.
        - 0 to 50: Good
        - 51 to 100: Moderate
        - 101 to 150: Unhealthy for Sensitive Groups
        - 151 to 200: Unhealthy
        - 201 to 300: Very Unhealthy
        - 301 and above: Hazardous
        
        ### 💡 Features Available:
        1. **AQI Prediction**: Predict AQI based on pollutant levels.
        2. **Real-Time AQI**: Get real-time AQI data for any location.
        3. **Hourly Trends**: View hourly AQI trends and predictions.
        4. **AQI Maps**: Visualize AQI hotspots in 3D.
        5. **Geolocation-Based Insights**: Discover AQI at your location.
        """
    )

# ------------------ Navigation Logic ------------------
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "📊 AQI Prediction",
        "📡 Real-Time AQI",
        "📈 AQI Trends",
        "🕒 Hourly AQI Trends",
        "🗺️ AQI Maps",
        "🔮 Forecast AQI",
        "📍 Geolocation-Based AQI Insights"
    ]
)

# ------------------ Home Section ------------------
if page == "🏠 Home":
    st.header("🌫️ Welcome to the AQI Prediction App")
    st.image(r'C:\Users\DELL\OneDrive\Desktop\JU\AQI-Prediction-App\jacek-dylag-wArzmoxD--Q-unsplash.jpg', use_column_width=True)
    st.success(f"📍 Current Location: {location_name} | Lat: {lat}, Lon: {lon}")

    # Plot Chandigarh AQI Data
    st.header("📡 Chandigarh AQI Levels")
    fig_chandigarh_aqi = px.scatter_mapbox(
        chandigarh_aqi_data,
        lat='lat',
        lon='lon',
        color='aqi',
        size='aqi',
        hover_name='location',
        color_continuous_scale='YlOrRd',
        size_max=15,
        zoom=12
    )
    fig_chandigarh_aqi.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_chandigarh_aqi)

# ------------------ AQI Prediction Section ------------------
elif page == "📊 AQI Prediction":
    st.header("🔮 AQI Prediction System")
    pm25 = st.number_input('PM2.5 (µg/m³)', 0.0, 500.0, 50.0)
    pm10 = st.number_input('PM10 (µg/m³)', 0.0, 500.0, 100.0)
    no = st.number_input('NO (µg/m³)', 0.0, 200.0, 5.0)
    no2 = st.number_input('NO2 (µg/m³)', 0.0, 200.0, 10.0)
    so2 = st.number_input('SO2 (µg/m³)', 0.0, 50.0, 10.0)
    o3 = st.number_input('Ozone (µg/m³)', 0.0, 300.0, 50.0)

    if st.button('🔮 Predict AQI'):
        features = np.array([pm25, pm10, no, no2, so2, o3]).reshape(1, -1)
        aqi_prediction = model.predict(features)[0]
        st.success(f"✅ Predicted AQI: {round(aqi_prediction, 2)}")

# ------------------ Real-Time AQI Section ------------------
elif page == "📡 Real-Time AQI":
    st.header("📡 Fetch Real-Time AQI")
    city = st.text_input("🌍 Enter City Name", "Delhi")

    if st.button('🔍 Fetch AQI'):
        url = f"https://api.waqi.info/feed/{city}/?token=350cda97252625ef7e032d3c8716e889cc2173a7"
        response = requests.get(url)
        data = response.json()
        
        if "data" in data:
            aqi_real_time = data['data']['aqi']
            st.success(f"🌫️ Real-Time AQI in {city}: {aqi_real_time}")
        else:
            st.error("❌ City not found or API limit exceeded. Please try again later.")

# ------------------ AQI Trends Section ------------------
elif page == "📈 AQI Trends":
    st.header("📈 Historical AQI Trends (Sample Data)")

    # Sample AQI Data
    df_trends = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=30),
        'AQI': np.random.randint(100, 300, 30)
    })

    # Plot AQI Trends
    fig_trend = px.line(df_trends, x='Date', y='AQI', title="📈 AQI Trends Over Time")
    st.plotly_chart(fig_trend)

# ------------------ Hourly AQI Trends Section ------------------
elif page == "🕒 Hourly AQI Trends":
    st.header("🕒 Hourly AQI Trends for Past 24 Hours")

    # Sample Hourly Data
    hourly_data = pd.DataFrame({
        'Time': pd.date_range(end=datetime.now(), periods=24, freq='H'),
        'AQI': np.random.randint(80, 200, 24)
    })

    fig_hourly_trends = px.line(hourly_data, x='Time', y='AQI', title="🕒 Hourly AQI Trends")
    st.plotly_chart(fig_hourly_trends)

# ------------------ AQI Maps Section ------------------
elif page == "🗺️ AQI Maps":
    st.header("🗺️ AQI Hotspot Maps")

    fig_map = px.scatter_mapbox(
        chandigarh_aqi_data,
        lat='lat',
        lon='lon',
        color='aqi',
        size='aqi',
        hover_name='location',
        color_continuous_scale='YlOrRd',
        size_max=15,
        zoom=12
    )
    fig_map.update_layout(
        mapbox_style="carto-positron",
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_map)

# ------------------ Forecast AQI Section ------------------
elif page == "🔮 Forecast AQI":
    st.header("🔮 Forecast Future AQI Using Time Series")

    # Load Sample Data
    aqi_df = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=60),
        'aqi': np.random.randint(100, 300, 60)
    })
    duration = st.selectbox("⏰ Select Duration for Forecast:", [30, 60, 90])

    if st.button("🔮 Generate Forecast"):
        model_arima = ARIMA(aqi_df['aqi'], order=(5, 1, 0))
        model_fit = model_arima.fit()
        forecast = model_fit.forecast(steps=duration)

        future_dates = [aqi_df['date'].max() + timedelta(days=i) for i in range(1, duration + 1)]
        forecast_df = pd.DataFrame({'Date': future_dates, 'Predicted AQI': forecast})

        fig_forecast = px.line(forecast_df, x='Date', y='Predicted AQI', title="🔮 AQI Forecast for Future Days")
        st.plotly_chart(fig_forecast)

# ------------------ Geolocation AQI Insights ------------------
elif page == "📍 Geolocation-Based AQI Insights":
    st.header("📍 Geolocation-Based AQI Insights")
    st.success(f"📍 Current Location: {location_name} | Lat: {lat}, Lon: {lon}")

    # Real-time AQI Scatter Plot
    fig_scatter_real_time = px.scatter_mapbox(
        chandigarh_aqi_data,
        lat='lat',
        lon='lon',
        color='aqi',
        size='aqi',
        hover_name='location',
        color_continuous_scale='YlOrRd',
        size_max=15,
        zoom=12
    )
    fig_scatter_real_time.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_scatter_real_time)

st.markdown("""<div class="footer">🌱 Developed with ❤️ by Sarika Sharma</div>""", unsafe_allow_html=True)

