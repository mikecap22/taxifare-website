import streamlit as st
import datetime
import requests
import numpy as np
import pandas as pd
from math import radians, sin, cos, sqrt, atan2


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

# Geo Coordinates
st.subheader("Pickup and Dropoff Locations (NYC bounds)")
col3, col4 = st.columns(2)
with col3:
    pickup_longitude = st.number_input('Pickup Longitude', format="%.6f", value= -73.987822)
    dropoff_longitude = st.number_input('Dropoff Longitude', format="%.6f", value= -73.966388)
with col4:
    pickup_latitude = st.number_input('Pickup Latitude', format="%.6f", value= 40.730006)
    dropoff_latitude = st.number_input('Dropoff Latitude', format="%.6f", value= 40.780006)

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
