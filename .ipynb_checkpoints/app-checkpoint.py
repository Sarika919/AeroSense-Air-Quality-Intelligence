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

# ------------------ Navbar and Styling ------------------
st.markdown(
    """
    <style>
        .navbar {
            background-color: #4CAF50;
            overflow: hidden;
            padding: 10px 20px;
        }
        .navbar a {
            float: left;
            display: block;
            color: white;
            text-align: center;
            padding: 12px 20px;
            text-decoration: none;
        }
        .navbar a:hover {
            background-color: #45a049;
        }
        .about-section {
            background-color: #f4f4f9;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
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

# ------------------ About Section ------------------
if st.button("ℹ️ About AQI"):
    st.markdown(
        """
        <div class='about-section'>
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
        </div>
        """,
        unsafe_allow_html=True
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

if page == "🏠 Home":
    st.header("🌫️ Welcome to the AQI Prediction App")
    st.image('images/climate-change-with-industrial-pollution.jpg', use_column_width=True)
    st.success("Explore features using the buttons above.")

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

elif page == "📡 Real-Time AQI":
    st.header("📡 Fetch Real-Time AQI")
    city = st.text_input("🌍 Enter City Name", "Delhi")

    if st.button('🔍 Fetch AQI'):
        url = f"https://api.waqi.info/feed/{city}/?token=YOUR_API_TOKEN"
        response = requests.get(url)
        data = response.json()
        
        if "data" in data:
            aqi_real_time = data['data']['aqi']
            st.success(f"🌫️ Real-Time AQI in {city}: {aqi_real_time}")
        else:
            st.error("❌ City not found or API limit exceeded. Please try again later.")

elif page == "📈 AQI Trends":
    st.header("📈 Historical AQI Trends with Insights")
    aqi_df = pd.read_csv('historical_aqi_data.csv')
    aqi_df['date'] = pd.to_datetime(aqi_df['date'])
    fig_trends = px.line(aqi_df, x='date', y='aqi', title="📊 AQI Trends Over Time")
    st.plotly_chart(fig_trends)

elif page == "🕒 Hourly AQI Trends":
    st.header("🕒 Hourly AQI Trends with Prediction")
    aqi_df = pd.read_csv('historical_aqi_data.csv')
    aqi_df['date'] = pd.to_datetime(aqi_df['date'])
    aqi_df['rolling_avg'] = aqi_df['aqi'].rolling(window=24, min_periods=1).mean()

    fig_hourly_trends = px.line(aqi_df, x='date', y='rolling_avg', title='📈 Hourly AQI Trends with Rolling Average')
    st.plotly_chart(fig_hourly_trends)

    duration = st.selectbox("⏰ Select Prediction Duration (Hours):", [24, 48, 72])

    if st.button("🔮 Generate Hourly Forecast"):
        aqi_df_prophet = aqi_df[['date', 'aqi']]
        aqi_df_prophet.columns = ['ds', 'y']

        model_prophet = Prophet()
        model_prophet.fit(aqi_df_prophet)

        future = model_prophet.make_future_dataframe(periods=duration, freq='H')
        forecast = model_prophet.predict(future)

        fig_forecast = px.line(forecast, x='ds', y='yhat', title=f"🔮 Hourly AQI Forecast for {duration} Hours")
        st.plotly_chart(fig_forecast)

elif page == "🗺️ AQI Maps":
    st.header("🗺️ Advanced 3D AQI Maps with Hotspots")
    aqi_data = pd.DataFrame({
        'city': ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad'],
        'lat': [28.61, 19.07, 22.57, 13.08, 12.97, 17.38, 18.52, 23.02],
        'lon': [77.23, 72.87, 88.36, 80.27, 77.59, 78.47, 73.85, 72.57],
        'aqi': [350, 120, 150, 100, 85, 135, 110, 95]
    })
    fig_hotspot = go.Figure(
        go.Densitymapbox(
            lat=aqi_data['lat'],
            lon=aqi_data['lon'],
            z=aqi_data['aqi'],
            radius=25,
            colorscale="YlOrRd",
            showscale=True
        )
    )
    fig_hotspot.update_layout(
        mapbox_style="stamen-terrain",
        mapbox_center_lat=20,
        mapbox_center_lon=78,
        mapbox_zoom=4,
        height=600
    )
    st.plotly_chart(fig_hotspot)

elif page == "🔮 Forecast AQI":
    st.header("🔮 Forecast Future AQI Using Time Series")
    aqi_df = pd.read_csv('historical_aqi_data.csv')
    duration = st.selectbox("⏰ Select Duration for Forecast:", [30, 60, 90])

    if st.button("🔮 Generate Forecast"):
        model_arima = ARIMA(aqi_df['aqi'], order=(5, 1, 0))
        model_fit = model_arima.fit()
        forecast = model_fit.forecast(steps=duration)

        future_dates = [aqi_df['date'].max() + timedelta(days=i) for i in range(1, duration + 1)]
        forecast_df = pd.DataFrame({'date': future_dates, 'aqi': forecast})

        fig_forecast = px.line(forecast_df, x='date', y='aqi', title=f"🔮 AQI Forecast for {duration} Days")
        st.plotly_chart(fig_forecast)

elif page == "📍 Geolocation-Based AQI Insights":
    st.header("📍 Geolocation-Based AQI Insights")
    geolocator = Nominatim(user_agent="aqi_app")
    location = geolocator.geocode("India")
    if location:
        lat, lon = location.latitude, location.longitude
        st.success(f"📍 Location Detected: {location.address} | Lat: {lat}, Lon: {lon}")
    else:
        st.error("❌ Location not found.")

st.markdown("""<style>.footer {position: fixed;bottom: 0;width: 100%;background-color: #4CAF50;color: white;text-align: center;padding: 10px;font-size: 14px;}</style>
<div class="footer">🌱 Developed with ❤️ by Sarika Sharma</div>""", unsafe_allow_html=True)

# import streamlit as st
# import pandas as pd
# import numpy as np
# import joblib
# import requests
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# from statsmodels.tsa.arima.model import ARIMA
# from prophet import Prophet
# from geopy.geocoders import Nominatim

# # ------------------ Load Trained Model ------------------
# model = joblib.load('aqi_model.pkl')

# # ------------------ Streamlit Page Configuration ------------------
# st.set_page_config(page_title="Advanced AQI Prediction", layout="wide")

# # ------------------ Web App Title ------------------
# st.title('🌫️ Advanced AQI Prediction App')
# st.markdown("#### 📡 Enter Air Pollutant Levels to Predict AQI and Compare with Real-Time Data")

# # ------------------ Sidebar Configuration ------------------
# st.sidebar.image('images/climate-change-with-industrial-pollution.jpg', use_column_width=True)
# st.sidebar.title("📚 Navigation")

# # ------------------ Dropdown for Navigation ------------------
# nav_option = st.sidebar.selectbox(
#     "Select a Section:",
#     [
#         "🏠 Home",
#         "📊 AQI Prediction",
#         "📡 Real-Time AQI",
#         "📈 AQI Trends",
#         "🕒 Hourly AQI Trends",
#         "🗺️ AQI Maps",
#         "🔮 Forecast AQI",
#         "📍 Geolocation-Based AQI Insights"
#     ]
# )

# # ------------------ Load Data or Generate Dummy if Missing ------------------
# @st.cache_data
# def load_data():
#     try:
#         df = pd.read_csv('historical_aqi_data.csv')
#         st.success("✅ Historical AQI Data Loaded Successfully!")
#     except FileNotFoundError:
#         st.warning("⚠️ historical_aqi_data.csv not found. Generating Sample Data...")
#         start_date = datetime(2024, 1, 1, 0)
#         date_range = [start_date + timedelta(hours=i) for i in range(90 * 24)]
#         aqi_values = np.random.randint(80, 300, size=90 * 24)
#         df = pd.DataFrame({'date': date_range, 'aqi': aqi_values})
#         df.to_csv('historical_aqi_data.csv', index=False)
#         st.success("✅ Auto-Generated historical_aqi_data.csv and Loaded Data!")
#     df['date'] = pd.to_datetime(df['date'])
#     return df

# # ------------------ Geolocation for AQI ------------------
# def get_location():
#     geolocator = Nominatim(user_agent="aqi_app")
#     location = geolocator.geocode("India")
#     if location:
#         return location.latitude, location.longitude, location.address
#     else:
#         return None, None, "Location not found"

# lat, lon, location_name = get_location()

# # ------------------ AQI Map Data (Sample for Demo) ------------------
# aqi_data = pd.DataFrame({
#     'city': ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad'],
#     'lat': [28.61, 19.07, 22.57, 13.08, 12.97, 17.38, 18.52, 23.02],
#     'lon': [77.23, 72.87, 88.36, 80.27, 77.59, 78.47, 73.85, 72.57],
#     'aqi': [350, 120, 150, 100, 85, 135, 110, 95]
# })

# # ------------------ Home Section ------------------
# if nav_option == "🏠 Home":
#     st.markdown(
#         """
#         ## 🌿 Welcome to the AQI Prediction App
#         - 🔍 **Predict AQI using pollutant values.**
#         - 📡 **Fetch real-time AQI data for any city.**
#         - 📈 **Analyze AQI trends and pollutants.**
#         - 🕒 **Visualize Hourly AQI Trends with Forecast.**
#         - 🗺️ **Explore 3D AQI Maps for Pollution Hotspots.**
#         """
#     )
#     st.image('images/climate-change-with-industrial-pollution.jpg', use_column_width=True, caption="Impact of Air Pollution")
#     st.success(f"📍 Location Detected: {location_name} | Lat: {lat}, Lon: {lon}")

# # ------------------ AQI Prediction Section ------------------
# elif nav_option == "📊 AQI Prediction":
#     st.header("🔮 AQI Prediction System")
#     st.markdown("### 🧪 Enter Pollutant Levels")

#     col1, col2, col3 = st.columns(3)
#     with col1:
#         pm25 = st.number_input('PM2.5 (µg/m³)', 0.0, 500.0, 50.0)
#         no = st.number_input('NO (µg/m³)', 0.0, 200.0, 5.0)
#     with col2:
#         pm10 = st.number_input('PM10 (µg/m³)', 0.0, 500.0, 100.0)
#         no2 = st.number_input('NO2 (µg/m³)', 0.0, 200.0, 10.0)
#     with col3:
#         so2 = st.number_input('SO2 (µg/m³)', 0.0, 50.0, 10.0)
#         o3 = st.number_input('Ozone (µg/m³)', 0.0, 300.0, 50.0)

#     if st.button('🔮 Predict AQI'):
#         features = np.array([pm25, pm10, no, no2, so2, o3]).reshape(1, -1)
#         aqi_prediction = model.predict(features)[0]
#         st.success(f"✅ Predicted AQI: {round(aqi_prediction, 2)}")

# # ------------------ Real-Time AQI ------------------
# elif nav_option == "📡 Real-Time AQI":
#     st.header("📡 Fetch Real-Time AQI")
#     city = st.text_input("🌍 Enter City Name", "Delhi")

#     if st.button('🔍 Fetch AQI'):
#         url = f"https://api.waqi.info/feed/{city}/?token=350cda97252625ef7e032d3c8716e889cc2173a7"
#         response = requests.get(url)
#         data = response.json()

#         if "data" in data:
#             aqi_real_time = data['data']['aqi']
#             st.success(f"🌫️ Real-Time AQI in {city}: {aqi_real_time}")
#         else:
#             st.error("❌ City not found or API limit exceeded. Please try again later.")

# # ------------------ AQI Trends Section ------------------
# elif nav_option == "📈 AQI Trends":
#     st.header("📈 Historical AQI Trends with Insights")
#     aqi_df = load_data()
#     fig_trends = px.line(aqi_df, x='date', y='aqi', title="📊 AQI Trends Over Time")
#     st.plotly_chart(fig_trends)

# # ------------------ Hourly AQI Trends Section ------------------
# elif nav_option == "🕒 Hourly AQI Trends":
#     st.header("🕒 Hourly AQI Trends with Prediction")
#     aqi_df = load_data()
#     aqi_df['rolling_avg'] = aqi_df['aqi'].rolling(window=24, min_periods=1).mean()

#     # Plot Hourly AQI Trends
#     fig_hourly_trends = px.line(aqi_df, x='date', y='rolling_avg', title='📈 Hourly AQI Trends with Rolling Average')
#     st.plotly_chart(fig_hourly_trends)

#     # Prophet Model for Hourly Prediction
#     duration = st.selectbox("⏰ Select Prediction Duration (Hours):", [24, 48, 72])

#     if st.button("🔮 Generate Hourly Forecast"):
#         aqi_df_prophet = aqi_df[['date', 'aqi']]
#         aqi_df_prophet.columns = ['ds', 'y']

#         model_prophet = Prophet()
#         model_prophet.fit(aqi_df_prophet)

#         future = model_prophet.make_future_dataframe(periods=duration, freq='H')
#         forecast = model_prophet.predict(future)

#         fig_forecast = px.line(forecast, x='ds', y='yhat', title=f"🔮 Hourly AQI Forecast for {duration} Hours")
#         st.plotly_chart(fig_forecast)

# # ------------------ AQI Maps Section ------------------
# elif nav_option == "🗺️ AQI Maps":
#     st.header("🗺️ Advanced 3D AQI Maps with Hotspots")
#     fig_hotspot = go.Figure(
#         go.Densitymapbox(
#             lat=aqi_data['lat'],
#             lon=aqi_data['lon'],
#             z=aqi_data['aqi'],
#             radius=25,
#             colorscale="YlOrRd",
#             showscale=True
#         )
#     )
#     fig_hotspot.update_layout(
#         mapbox_style="stamen-terrain",
#         mapbox_center_lat=20,
#         mapbox_center_lon=78,
#         mapbox_zoom=4,
#         height=600
#     )
#     st.plotly_chart(fig_hotspot)

# # ------------------ AQI Forecast Section ------------------
# elif nav_option == "🔮 Forecast AQI":
#     st.header("🔮 Forecast Future AQI Using Time Series")
#     aqi_df = load_data()
#     duration = st.selectbox("⏰ Select Duration for Forecast:", [30, 60, 90])

#     if st.button("🔮 Generate Forecast"):
#         model_arima = ARIMA(aqi_df['aqi'], order=(5, 1, 0))
#         model_fit = model_arima.fit()
#         forecast = model_fit.forecast(steps=duration)

#         future_dates = [aqi_df['date'].max() + timedelta(days=i) for i in range(1, duration + 1)]
#         forecast_df = pd.DataFrame({'date': future_dates, 'aqi': forecast})

#         fig_forecast = px.line(forecast_df, x='date', y='aqi', title=f"🔮 AQI Forecast for {duration} Days")
#         st.plotly_chart(fig_forecast)

# # ------------------ Geolocation-Based AQI Insights ------------------
# elif nav_option == "📍 Geolocation-Based AQI Insights":
#     st.header("📍 Geolocation-Based AQI Insights")
#     st.success(f"📍 Location: {location_name} | Lat: {lat}, Lon: {lon}")
#     st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))


# # ================== Import Libraries ==================
# import streamlit as st
# import pandas as pd
# import numpy as np
# import joblib
# import requests
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# from statsmodels.tsa.arima.model import ARIMA
# from prophet import Prophet
# from geopy.geocoders import Nominatim

# # ================== Load Trained Model ==================
# model = joblib.load('aqi_model.pkl')

# # ================== Streamlit Page Configuration ==================
# st.set_page_config(page_title="🌫️ AQI Prediction Dashboard", layout="wide")

# # ================== Web App Title ==================
# st.markdown("""
#     <style>
#         .main-title {
#             font-size: 40px;
#             color: #4CAF50;
#             font-weight: bold;
#         }
#         .sub-title {
#             font-size: 18px;
#             color: #555;
#         }
#     </style>
# """, unsafe_allow_html=True)

# st.markdown("<div class='main-title'>🌫️ Advanced AQI Prediction Dashboard</div>", unsafe_allow_html=True)
# st.markdown("<div class='sub-title'>📡 Predict, Visualize & Analyze Air Quality Data Like a Pro!</div>", unsafe_allow_html=True)

# # ================== Sidebar Configuration ==================
# st.sidebar.image('images/climate-change-with-industrial-pollution.jpg', use_column_width=True)
# st.sidebar.title("📚 Navigation")

# # ================== Dropdown for Navigation ==================
# nav_option = st.sidebar.selectbox(
#     "Select a Section:",
#     [
#         "🏠 Home",
#         "📊 AQI Prediction",
#         "📡 Real-Time AQI",
#         "📈 AQI Trends",
#         "🕒 Hourly AQI Trends",
#         "🗺️ AQI Maps",
#         "🔮 Forecast AQI",
#         "📍 Geolocation-Based AQI Insights"
#     ]
# )

# # ================== Load Data or Generate Dummy if Missing ==================
# @st.cache_data
# def load_data():
#     try:
#         df = pd.read_csv('historical_aqi_data.csv')
#         st.success("✅ Historical AQI Data Loaded Successfully!")
#     except FileNotFoundError:
#         st.warning("⚠️ historical_aqi_data.csv not found. Generating Sample Data...")
#         start_date = datetime(2024, 1, 1, 0)
#         date_range = [start_date + timedelta(hours=i) for i in range(90 * 24)]
#         aqi_values = np.random.randint(80, 300, size=90 * 24)
#         df = pd.DataFrame({'date': date_range, 'aqi': aqi_values})
#         df.to_csv('historical_aqi_data.csv', index=False)
#         st.success("✅ Auto-Generated historical_aqi_data.csv and Loaded Data!")
#     df['date'] = pd.to_datetime(df['date'])
#     return df

# # ================== Geolocation for AQI ==================
# def get_location():
#     geolocator = Nominatim(user_agent="aqi_app")
#     location = geolocator.geocode("India")
#     if location:
#         return location.latitude, location.longitude, location.address
#     else:
#         return None, None, "Location not found"

# lat, lon, location_name = get_location()

# # ================== AQI Map Data ==================
# aqi_data = pd.DataFrame({
#     'city': ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 'Hyderabad', 'Pune', 'Ahmedabad'],
#     'lat': [28.61, 19.07, 22.57, 13.08, 12.97, 17.38, 18.52, 23.02],
#     'lon': [77.23, 72.87, 88.36, 80.27, 77.59, 78.47, 73.85, 72.57],
#     'aqi': [350, 120, 150, 100, 85, 135, 110, 95]
# })

# # ================== Home Section ==================
# if nav_option == "🏠 Home":
#     st.markdown(
#         """
#         ## 🌿 Welcome to the AQI Prediction App
#         - 🔍 **Predict AQI using pollutant values.**
#         - 📡 **Fetch real-time AQI data for any city.**
#         - 📈 **Analyze AQI trends and pollutants.**
#         - 🕒 **Visualize Hourly AQI Trends with Forecast.**
#         - 🗺️ **Explore 3D AQI Maps for Pollution Hotspots.**
#         """
#     )
#     st.image('images/climate-change-with-industrial-pollution.jpg', use_column_width=True, caption="Impact of Air Pollution")
#     st.success(f"📍 Location Detected: {location_name} | Lat: {lat}, Lon: {lon}")

# # ================== AQI Prediction Section ==================
# elif nav_option == "📊 AQI Prediction":
#     st.header("🔮 AQI Prediction System")
#     st.markdown("### 🧪 Enter Pollutant Levels")

#     col1, col2, col3 = st.columns(3)
#     with col1:
#         pm25 = st.number_input('PM2.5 (µg/m³)', 0.0, 500.0, 50.0)
#         no = st.number_input('NO (µg/m³)', 0.0, 200.0, 5.0)
#     with col2:
#         pm10 = st.number_input('PM10 (µg/m³)', 0.0, 500.0, 100.0)
#         no2 = st.number_input('NO2 (µg/m³)', 0.0, 200.0, 10.0)
#     with col3:
#         so2 = st.number_input('SO2 (µg/m³)', 0.0, 50.0, 10.0)
#         o3 = st.number_input('Ozone (µg/m³)', 0.0, 300.0, 50.0)

#     if st.button('🔮 Predict AQI'):
#         features = np.array([pm25, pm10, no, no2, so2, o3]).reshape(1, -1)
#         aqi_prediction = model.predict(features)[0]
#         st.success(f"✅ Predicted AQI: {round(aqi_prediction, 2)}")

# # ================== Real-Time AQI Section ==================
# elif nav_option == "📡 Real-Time AQI":
#     st.header("📡 Fetch Real-Time AQI")
#     city = st.text_input("🌍 Enter City Name", "Delhi")

#     if st.button('🔍 Fetch AQI'):
#         url = f"https://api.waqi.info/feed/{city}/?token=350cda97252625ef7e032d3c8716e889cc2173a7"
#         response = requests.get(url)
#         data = response.json()

#         if "data" in data:
#             aqi_real_time = data['data']['aqi']
#             st.success(f"🌫️ Real-Time AQI in {city}: {aqi_real_time}")
#         else:
#             st.error("❌ City not found or API limit exceeded. Please try again later.")

# # ================== AQI Maps Section ==================
# elif nav_option == "🗺️ AQI Maps":
#     st.header("🗺️ Explore 3D AQI Maps with Pollution Hotspots")
#     fig_hotspot = go.Figure(
#         go.Densitymapbox(
#             lat=aqi_data['lat'],
#             lon=aqi_data['lon'],
#             z=aqi_data['aqi'],
#             radius=25,
#             colorscale="YlOrRd",
#             showscale=True
#         )
#     )
#     fig_hotspot.update_layout(
#         mapbox_style="carto-positron",
#         mapbox_center_lat=20,
#         mapbox_center_lon=78,
#         mapbox_zoom=4,
#         height=600
#     )
#     st.plotly_chart(fig_hotspot)

# # ================== Geolocation-Based AQI Insights ==================
# elif nav_option == "📍 Geolocation-Based AQI Insights":
#     st.header("📍 Geolocation-Based AQI Insights")
#     st.success(f"📍 Location: {location_name} | Lat: {lat}, Lon: {lon}")
#     st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

# st.markdown("<div style='text-align: center; color: grey;'>🚀 Developed with ❤️ by Sarika Sharma</div>", unsafe_allow_html=True)
