import streamlit as st
import datetime
import requests
import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


st.set_page_config(
    page_title="Main Estimator",
    page_icon="🚕",
)
# '''
# # TaxiFareModel
# '''
st.header(''' Welcome to my TaxiFare Model App''')

st.image(
    "https://publish.purewow.net/wp-content/uploads/sites/2/2018/05/nyc-yellow-taxi-in-times-square-hero.jpg",
    caption="New York City Taxi in Times Square",
    use_column_width=True # Ensures the image scales nicely with the window
)

st.write('''
 Use this page to get a real-time fare estimate by filling out the ride parameters below.
''')


# '''
# st.markdown(
# Remember that there are several ways to output content into your web page...

# Either as with the title by just creating a string (or an f-string). Or as with this paragraph using the `st.` functions
# ) '''

# '''
# ## Here we would like to add some controllers in order to ask the user to select the parameters of the ride


# 1. Let's ask for:
# - date and time
# - pickup longitude
# - pickup latitude
# - dropoff longitude
# - dropoff latitude
# - passenger count
# '''

@st.cache_data
def geocode_address(address, timeout=10):
    """
    Converts a human-readable address into (latitude, longitude) coordinates,
    with a bias towards New York City.
    """
    if not address:
        return None, None

    geolocator = Nominatim(user_agent="nyc_taxi_app_v1", timeout=timeout)

    try:
        # Bounding box for NYC: (-74.25909, 40.477399, -73.70018, 40.917577)
        location = geolocator.geocode(
            address,
            viewbox=[-74.25, 40.47, -73.70, 40.91],
            bounded=True
        )

        if location:
            return location.latitude, location.longitude
        else:
            return None, None

    except GeocoderTimedOut:
        st.error("Geocoding service timed out; Please try again.")
        return None, None
    except GeocoderServiceError as e:
        st.error(f"Geocoding service error: {e}")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred during geocoding: {e}")
        return None, None

st.markdown('''
## Select the parameters for your ride
''')
# Date and Time
st.subheader("Ride Details")
col1, col2 = st.columns(2)
with col1:
    date = st.date_input('Date', datetime.date.today())
with col2:
    time = st.time_input('Time', datetime.time(12, 00))

# Geo Coordinates 1

# --- Coordinate Session State Initialization ---
# Use the user's existing default values
default_p_lon = -73.987822
default_d_lon = -73.966388
default_p_lat = 40.730006
default_d_lat = 40.780006

# Initialize session state for coordinates if they don't exist
if 'p_lon' not in st.session_state:
    st.session_state['p_lon'] = default_p_lon
    st.session_state['d_lon'] = default_d_lon
    st.session_state['p_lat'] = default_p_lat
    st.session_state['d_lat'] = default_d_lat

st.subheader("Pickup and Dropoff Locations (NYC bounds)")


input_mode = st.radio(
    "Choose Location Input Method:",
    ("Direct Coordinate Input", "Address Input (with Geocoding)"),
    horizontal=True
)
# col3, col4 = st.columns(2)
# with col3:
#     pickup_longitude = st.number_input('Pickup Longitude', format="%.6f", value= -73.987822)
#     dropoff_longitude = st.number_input('Dropoff Longitude', format="%.6f", value= -73.966388)
# with col4:
#     pickup_latitude = st.number_input('Pickup Latitude', format="%.6f", value= 40.730006)
#     dropoff_latitude = st.number_input('Dropoff Latitude', format="%.6f", value= 40.780006)

# --- Conditional Input Blocks ---

if input_mode == "Direct Coordinate Input":
    # User's original coordinate inputs, but now they update st.session_state
    col3, col4 = st.columns(2)
    with col3:
        st.session_state['p_lon'] = st.number_input(
            'Pickup Longitude',
            format="%.6f",
            value=st.session_state['p_lon']
        )
        st.session_state['d_lon'] = st.number_input(
            'Dropoff Longitude',
            format="%.6f",
            value=st.session_state['d_lon']
        )
    with col4:
        st.session_state['p_lat'] = st.number_input(
            'Pickup Latitude',
            format="%.6f",
            value=st.session_state['p_lat']
        )
        st.session_state['d_lat'] = st.number_input(
            'Dropoff Latitude',
            format="%.6f",
            value=st.session_state['d_lat']
        )

elif input_mode == "Address Input (with Geocoding)":
    # New Address inputs
    start_address = st.text_input(
        "Starting Address",
        "5th Avenue and 42nd Street, New York"
    )
    end_address = st.text_input(
        "Ending Address",
        "JFK Airport, New York"
    )

    if st.button("Convert Addresses and Update Coordinates"):
        with st.spinner('Converting addresses to coordinates...'):
            p_lat_new, p_lon_new = geocode_address(start_address)
            d_lat_new, d_lon_new = geocode_address(end_address)

            if p_lat_new and p_lon_new and d_lat_new and d_lon_new:
                # Update session state with new geocoded values
                st.session_state['p_lat'] = p_lat_new
                st.session_state['p_lon'] = p_lon_new
                st.session_state['d_lat'] = d_lat_new
                st.session_state['d_lon'] = d_lon_new
                st.success("Addresses converted and coordinates updated for calculation!")
            else:
                st.error("Could not find coordinates for one or both addresses. Using current coordinates.")


# --- Coordinate Variable Assignment (for downstream compatibility) ---
# We define the variables the rest of the code expects using the current session state values.
pickup_longitude = st.session_state['p_lon']
dropoff_longitude = st.session_state['d_lon']
pickup_latitude = st.session_state['p_lat']
dropoff_latitude = st.session_state['d_lat']

# Passenger Count
passenger_count = st.slider('Passenger Count', 1, 8, 1)


# '''
# ## Once we have these, let's call our API in order to retrieve a prediction

# See ? No need to load a `model.joblib` file in this app, we do not even need to know anything about Data Science in order to retrieve a prediction...

# 🤔 How could we call our API ? Off course... The `requests` package 💡
# '''



# Personal Added Features #
st.markdown("### Estimated Route")

# 1. Create a DataFrame for st.map
map_data = pd.DataFrame({
    'latitude': [pickup_latitude, dropoff_latitude],
    'longitude': [pickup_longitude, dropoff_longitude]
})

# 2. Display the map
st.map(map_data, zoom=9)


st.markdown('''
## Get Prediction
''')

url = 'https://taxifare.lewagon.ai/predict'

# if url == 'https://taxifare.lewagon.ai/predict':

#     st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

# '''

# 2. Let's build a dictionary containing the parameters for our API...

# 3. Let's call our API using the `requests` package...

# 4. Let's retrieve the prediction from the **JSON** returned by the API...

# ## Finally, we can display the prediction to the user
# '''

if st.button('Estimate Fare'):
    # 1. Build dictionary containing the parameters
    pickup_datetime_raw = datetime.datetime.combine(date, time)
    pickup_datetime_formatted = pickup_datetime_raw.strftime("%Y-%m-%d %H:%M:%S")

    params = {
        'pickup_datetime': pickup_datetime_formatted,
        'pickup_longitude': pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude': dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
    }

    # Display loading spinner while waiting for API response
    with st.spinner('Calculating fare...'):
        # 2. Call the API using requests
        try:
            response = requests.get(url, params=params)

            # 3. Retrieve the prediction
            if response.status_code == 200:
                prediction = response.json()
                fare = prediction.get('fare', 'N/A')

                # Display the prediction
                st.success(f"### Estimated Taxi Fare: **${fare:.2f}**")
                st.balloons()
            else:
                st.error(f"Error calling the API. Status code: {response.status_code}. Response: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred during the API request: {e}")


# Another personal addition #

# --- Distance and CO2 Estimation ---

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great-circle distance in kilometers and miles between two points
    on the Earth (specified in decimal degrees).
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    R_km = 6371  # Radius of Earth in kilometers
    distance_km = R_km * c

    miles_per_km = 0.621371
    distance_miles = distance_km * miles_per_km

    return distance_km, distance_miles


# Calculate distance
distance_km, distance_miles = haversine(
    pickup_longitude, pickup_latitude,
    dropoff_longitude, dropoff_latitude
)

st.markdown("---")
st.markdown("### Route Metrics")

# Display distance
col_dist1, col_dist2, col_dist3 = st.columns(3)

col_dist1.metric("Distance (Miles)", f"{distance_miles:.2f} mi")
col_dist2.metric("Distance (Kilometers)", f"{distance_km:.2f} km")

# Mock CO2 Estimation (e.g., 0.15 kg CO2 per km for a city taxi)
co2_per_km = 0.15
co2_estimate_kg = distance_km * co2_per_km

col_dist3.metric("CO₂ Estimate", f"{co2_estimate_kg:.2f} kg", "- Low Emission")

# Added video playing NY related theme music #

YOUTUBE_URL = "https://www.youtube.com/watch?v=vk6014HuxcE"
st.video(YOUTUBE_URL)
