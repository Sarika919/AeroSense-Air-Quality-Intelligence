
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

# ------------------ Navbar ------------------st.markdown(
st.markdown( """
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
        <a href="#aqi-overview">📊 AQI Overview</a>
        <a href="#geolocation">📍 Geolocation-Based AQI Insights</a>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ Geolocation ------------------
def get_location():
    geolocator = Nominatim(user_agent="aqi_app", timeout=10)
    location = geolocator.geocode("Chandigarh, India")
    if location:
        return location.latitude, location.longitude, location.address
    else:
        return 30.7333, 76.7794, "Chandigarh, India"


lat, lon, location_name = get_location()

# ------------------ Sample AQI Data for Chandigarh ------------------
chandigarh_aqi_data = pd.DataFrame({
    'location': ['Sector 17', 'Sector 22', 'Sector 35', 'Manimajra', 'ISBT 43', 'Industrial Area', 'Sector 8', 'Sector 10'],
    'lat': [30.7352, 30.7280, 30.7160, 30.7190, 30.7056, 30.7053, 30.7534, 30.7611],
    'lon': [76.7725, 76.7794, 76.7415, 76.8361, 76.8000, 76.8019, 76.7851, 76.7736],
    'aqi': [180, 150, 135, 190, 160, 200, 120, 130]
})

# ------------------ Navigation ------------------
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

# ------------------ Home ------------------
if page == "🏠 Home":
    st.header("🌫️ Welcome to the AQI Prediction App")
    with st.expander("📘 How AQI Forecasting Works"):
        st.markdown("""
        AQI Forecasting is based on **Time Series Analysis** of historical data.

        - We're using **Prophet Model (by Facebook)** here, which is effective for trends and seasonality detection.
        - Input: Daily AQI values
        - Output: Predicted AQI for next 30/60/90 days

        **Real-world models** also take into account:
        - Meteorological data (temperature, humidity, wind speed)
        - Emission sources (industrial, vehicular)
        - Geographical patterns

        The prediction is **not exact**, but gives a reliable estimate for planning and alerts.
        """)
    st.image("jacek-dylag-wArzmoxD--Q-unsplash.jpg", use_container_width=True)
    st.success(f"📍 Current Location: {location_name} | Lat: {lat}, Lon: {lon}")

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
    fig_chandigarh_aqi.update_layout(mapbox_style="open-street-map", height=500, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_chandigarh_aqi)
    

# ------------------ AQI Prediction ------------------
elif page == "📊 AQI Prediction":
    st.header("🔮 AQI Prediction System")

    # User inputs for pollutants
    st.subheader("Enter Pollutant Concentration Values:")
    pm25 = st.number_input('PM2.5 (µg/m³)', 0.0, 500.0, 50.0)
    pm10 = st.number_input('PM10 (µg/m³)', 0.0, 500.0, 100.0)
    no = st.number_input('NO (µg/m³)', 0.0, 200.0, 5.0)
    no2 = st.number_input('NO2 (µg/m³)', 0.0, 200.0, 10.0)
    so2 = st.number_input('SO2 (µg/m³)', 0.0, 50.0, 10.0)
    o3 = st.number_input('Ozone (µg/m³)', 0.0, 300.0, 50.0)
    co = st.number_input('CO (µg/m³)', 0.0, 10.0, 0.5)
    benzene = st.number_input('Benzene (µg/m³)', 0.0, 10.0, 0.5)
    toluene = st.number_input('Toluene (µg/m³)', 0.0, 10.0, 0.5)
    xylene = st.number_input('Xylene (µg/m³)', 0.0, 10.0, 0.5)
    nh3 = st.number_input('Ammonia (NH3) (µg/m³)', 0.0, 200.0, 5.0)
    temperature = st.number_input('Temperature (°C)', -10.0, 50.0, 25.0)

    # AQI Calculation Function
    def calculate_aqi(pollutant_value, C_low, C_high, I_low, I_high):
        return ((pollutant_value - C_low) / (C_high - C_low)) * (I_high - I_low) + I_low

    # Example AQI for PM2.5 (more pollutants can be added similarly)
    pm25_aqi = calculate_aqi(pm25, 0, 12, 0, 50)  # Example for PM2.5 (adjust ranges based on your data)

    # Trigger AQI prediction on button click
    if st.button('🔮 Predict AQI', key="predict_button"):  # Added a unique key here
        # Model prediction (assuming 'model' is already defined in the script)
        features = np.array([pm25, pm10, no, no2, so2, o3, co, benzene, toluene, xylene, nh3, temperature]).reshape(1, -1)
        aqi_prediction = model.predict(features)[0]
        st.success(f"✅ Predicted AQI: {round(aqi_prediction, 2)}")
        
        
# ------------------ Real-Time AQI ------------------
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

# ------------------ AQI Trends ------------------
elif page == "📈 AQI Trends":
    st.header("📈 Historical AQI Trends (Sample Data)")
    df_trends = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=30),
        'AQI': np.random.randint(100, 300, 30)
    })
    fig_trend = px.line(df_trends, x='Date', y='AQI', title="📈 AQI Trends Over Time")
    st.plotly_chart(fig_trend)

# ------------------ Hourly AQI Trends ------------------
elif page == "🕒 Hourly AQI Trends":
    st.header("🕒 Hourly AQI Trends for Past 24 Hours")
    hourly_data = pd.DataFrame({
        'Time': pd.date_range(end=datetime.now(), periods=24, freq='H'),
        'AQI': np.random.randint(80, 200, 24)
    })
    fig_hourly_trends = px.line(hourly_data, x='Time', y='AQI', title="🕒 Hourly AQI Trends")
    st.plotly_chart(fig_hourly_trends)

# ------------------ AQI Maps ------------------
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
    fig_map.update_layout(mapbox_style="carto-positron", height=500, margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map)

# ------------------ Forecast AQI ------------------
elif page == "🔮 Forecast AQI":
    st.header("🔮 Forecast Future AQI Using Time Series")
    aqi_df = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=60),
        'aqi': np.random.randint(100, 300, 60)
    })

    duration = st.selectbox("⏰ Select Duration for Forecast:", [30, 60, 90])

    if st.button("🔮 Generate Forecast"):
        df_prophet = aqi_df.rename(columns={'date': 'ds', 'aqi': 'y'})
        prophet_model = Prophet()
        prophet_model.fit(df_prophet)

        future = prophet_model.make_future_dataframe(periods=duration)
        forecast = prophet_model.predict(future)

        fig_forecast = px.line(forecast, x='ds', y='yhat', title='🔮 Forecasted AQI')
        st.plotly_chart(fig_forecast)

# # ------------------ Geolocation AQI ------------------
# elif page == "📍 Geolocation-Based AQI Insights":
#     st.header("📍 AQI Insights Based on Your Location")
#     st.success(f"Your Location: {location_name} (Lat: {lat}, Lon: {lon})")

#     st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
#     st.write("🔍 Fetching nearby AQI hotspots...")

#     nearest = chandigarh_aqi_data.copy()
#     nearest['distance'] = np.sqrt((nearest['lat'] - lat)**2 + (nearest['lon'] - lon)**2)
#     nearest = nearest.sort_values(by='distance').head(5)

#     st.write("🧭 Nearest AQI Locations:")
#     st.dataframe(nearest[['location', 'aqi']])
# ------------------ Geolocation AQI ------------------
elif page == "📍 Geolocation-Based AQI Insights":
    st.header("📍 AQI Insights Based on Your Location")
    st.success(f"Your Location: {location_name} (Lat: {lat}, Lon: {lon})")

    # Show map with current location
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

    st.write("🔍 Fetching nearby AQI hotspots...")

    # Calculate nearest AQI points
    nearest = chandigarh_aqi_data.copy()
    nearest['distance'] = np.sqrt((nearest['lat'] - lat)**2 + (nearest['lon'] - lon)**2)
    nearest = nearest.sort_values(by='distance').head(5)

    # Display nearest hotspots
    st.subheader("📍 Nearest AQI Monitoring Locations")
    st.dataframe(nearest[['location', 'aqi', 'distance']])

    # Plot AQI bar chart for nearest locations
    fig_nearest = px.bar(
        nearest,
        x='location',
        y='aqi',
        color='aqi',
        color_continuous_scale='YlOrRd',
        title="🌫️ AQI Levels at Nearby Locations"
    )
<<<<<<< HEAD
    fig_scatter_real_time.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_scatter_real_time)

st.markdown("""<div class="footer">🌱 Developed with ❤️ by Sarika Sharma</div>""", unsafe_allow_html=True)

=======
    st.plotly_chart(fig_nearest)
>>>>>>> 9ba0103 (Save all local changes before pulling)
