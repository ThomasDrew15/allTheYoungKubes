from typing import Optional, Dict, Tuple, List, Any

import streamlit as st
import requests
import time
import numpy as np
from collections import Counter

from prometheus_client import start_http_server, Counter
import random

# Create a Prometheus counter metric
c = Counter('my_app_requests', 'Total number of requests')

def handle_request():
    c.inc()  # Increment the request counter
    # Simulate some application logic
    time.sleep(random.randint(1, 5))

# Start an HTTP server to expose metrics
start_http_server(8000)

while True:
    handle_request()


def get_weather_icon_html(icon_code: str) -> str:
    """
    Input
        - icon_code: A string representing the weather icon code from the API.
    Precondition
        - `icon_code` is a valid string obtained from the weather API response.
    Output
        - A string containing HTML for displaying the weather icon.
    Postcondition
        - The returned HTML string correctly references the weather icon using the provided `icon_code`.
    Invariant
        - The base URL for icons remains constant and valid.
    Assumptions
        - The `icon_code` corresponds to an existing icon on the server.
    Side Effects
        - None
    """
    base_url = "https://openweathermap.org/img/wn/"
    return f'<img src="{base_url}{icon_code}@2x.png" width="50">'


def send_request(url: str, method: str = 'GET', json_data: Optional[dict] = None) -> Optional[requests.Response]:
    """
    Input
        - url: A string representing the API endpoint.
        - method: An optional string representing the HTTP method, default is 'GET'.
        - json_data: An optional dictionary containing data to be sent in the request body (for POST requests).
    Precondition
        - `url` is a valid API endpoint.
        - `method` is either 'GET' or 'POST'.
        - `json_data` is a dictionary if provided.
    Output
        - A Response object if the request is successful, or None if an error occurs.
    Postcondition
        - A successful HTTP request returns a valid Response object.
        - In case of failure, an error is logged, and None is returned.
    Invariant
        - None
    Assumptions
        - The network connection is available.
        - The API endpoint is responsive.
    Side Effects
        - A request is sent over the network, potentially consuming bandwidth and incurring delays.
    """
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=json_data, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"HTTP request failed: {e}")
        response = None
    return response


def show_loading_bar(message: str, total: int = 100) -> None:
    """
    Input
        - message: A string representing the message to display with the loading bar.
        - total: An integer representing the total number of iterations, default is 100.
    Precondition
        - `message` is a non-empty string.
        - `total` is a positive integer.
    Output
        - None (this function directly updates the UI).
    Postcondition
        - A loading bar is displayed in the Streamlit app with the provided message, updating incrementally.
    Variant
        - The value of `total` decreases with each iteration, ensuring eventual termination.
    Side Effects
        - Updates the UI with a progress bar, consuming CPU time and potentially blocking other operations momentarily.
    """
    progress_bar = st.progress(0, text=message)
    for percent in range(total):
        time.sleep(0.01)
        progress_bar.progress(percent + 1, text=message)
    progress_bar.empty()


def format_outfit_suggestions(suggestions: Dict[str, str]) -> str:
    """
    Input
        - suggestions: A dictionary containing clothing recommendations (keys: 'Top', 'Bottom', 'Footwear', 'Outerwear', 'Accessories').
    Precondition
        - `suggestions` is a dictionary with the expected keys and corresponding values as strings.
    Output
        - A formatted HTML string representing the outfit suggestions.
    Postcondition
        - The returned string correctly formats and presents the outfit suggestions in HTML.
    Invariant
        - The HTML structure remains consistent for all sets of suggestions.
    Side Effects
        - None
    """
    return f"""
    <div class="response-info">
        <strong>Top:</strong> {suggestions['Top']}<br>
        <strong>Bottom:</strong> {suggestions['Bottom']}<br>
        <strong>Footwear:</strong> {suggestions['Footwear']}<br>
        <strong>Outerwear:</strong> {suggestions['Outerwear']}<br>
        <strong>Accessories:</strong> {suggestions['Accessories']}<br>
    </div>
    """


from typing import Tuple

def process_weather_data(weather_data: dict) -> Tuple[float, float, float, str]:
    """
    Input
        - weather_data: A dictionary representing the weather forecast data returned by the weather API.
    Precondition
        - `weather_data` is a dictionary containing a 'list' key with weather forecast entries.
    Output
        - A tuple containing average temperature (float), average humidity (float), average wind speed (float), and the most common weather condition (string).
    Postcondition
        - The returned tuple contains correctly calculated averages and the most common weather condition from the provided data.
    Invariant
        - The length of the `temps`, `humidities`, `wind_speeds`, and `weather_main_conditions` lists is equal.
    Side Effects
        - None
    """
    temps, humidities, wind_speeds, weather_main_conditions = [], [], [], []

    for forecast in weather_data['list']:
        temps.append(forecast['main']['temp'])
        humidities.append(forecast['main']['humidity'])
        wind_speeds.append(forecast['wind']['speed'])
        weather_main_conditions.append(forecast['weather'][0]['main'])

    avg_temp = float(np.mean(temps))
    avg_humidity = float(np.mean(humidities))
    avg_wind_speed = float(np.mean(wind_speeds))
    most_common_weather: str = Counter(weather_main_conditions).most_common(1)[0][0]

    return avg_temp, avg_humidity, avg_wind_speed, most_common_weather



def display_weather_summary(avg_temp: float, avg_humidity: float, avg_wind_speed: float, most_common_weather: str) -> None:
    """
    Input
        - avg_temp: A float representing the average temperature.
        - avg_humidity: A float representing the average humidity.
        - avg_wind_speed: A float representing the average wind speed.
        - most_common_weather: A string representing the most common weather condition.
    Precondition
        - `avg_temp`, `avg_humidity`, and `avg_wind_speed` are float values.
        - `most_common_weather` is a string representing a valid weather condition.
    Output
        - None (this function directly updates the UI).
    Postcondition
        - The weather summary is correctly displayed in the Streamlit app.
    Invariant
        - The summary displays consistent styling and formatting regardless of the data values.
    Side Effects
        - Updates the Streamlit UI with a weather summary.
    """
    st.subheader("Average weather over the next 24 hours")
    st.markdown(f"""
        <div class="weather-info">
            <span>Most Common Weather: {most_common_weather}</span>
            <i class="fas fa-cloud icon" style="color:gray;"></i>
        </div>
        <div class="weather-info">
            <span>Average Temperature: {avg_temp:.2f} °C</span>
            <i class="fas fa-thermometer-half icon" style="color:orange;"></i>
        </div>
        <div class="weather-info">
            <span>Average Humidity: {avg_humidity:.2f}%</span>
            <i class="fas fa-tint icon" style="color:blue;"></i>
        </div>
        <div class="weather-info">
            <span>Average Wind Speed: {avg_wind_speed:.2f} m/s</span>
            <i class="fas fa-wind icon" style="color:green;"></i>
        </div>
    """, unsafe_allow_html=True)


def display_forecasts(forecasts: List[dict]) -> None:
    """
    Input
        - forecasts: A list of dictionaries, each representing a three-hourly weather forecast.
    Precondition
        - `forecasts` is a list of dictionaries, each containing keys such as 'dt_txt', 'weather', 'main', and 'wind'.
    Output
        - None (this function directly updates the UI).
    Postcondition
        - Detailed three-hourly forecasts are displayed in the Streamlit app, each expandable to show more details.
    Invariant
        - Each forecast is displayed with the correct corresponding icon, temperature, humidity, and wind speed.
    Side Effects
        - Updates the Streamlit UI with detailed weather forecasts.
    """
    st.subheader("Three Hourly Forecasts (Click to Expand)")
    for forecast in forecasts:
        dt_txt = forecast['dt_txt']
        with st.expander(f"Details for {dt_txt}"):
            if 'weather' in forecast:
                weather = forecast['weather'][0]
                icon_html = get_weather_icon_html(weather['icon'])
                st.markdown(f"""
                    <div class="weather-info">
                        Weather: {weather['main']} - {weather['description'].capitalize()}
                        {icon_html}
                    </div>
                """, unsafe_allow_html=True)

            if 'main' in forecast:
                temp_celsius = forecast['main']['temp']
                st.markdown(f"""
                    <div class="weather-info">
                        Temperature: {temp_celsius} °C
                        <i class="fas fa-temperature-high icon" style="color:orange;"></i>
                    </div>
                """, unsafe_allow_html=True)

                humidity_percent = forecast['main']['humidity']
                st.markdown(f"""
                    <div class="weather-info">
                        Humidity: {humidity_percent}%
                        <i class="fas fa-tint icon" style="color:orange;"></i>
                    </div>
                """, unsafe_allow_html=True)

            if 'wind' in forecast:
                wind_speed_ms = forecast['wind']['speed']
                st.markdown(f"""
                    <div class="weather-info">
                        Wind Speed: {wind_speed_ms} m/s
                        <i class="fas fa-wind icon" style="color:green;"></i>
                    </div>
                """, unsafe_allow_html=True)


def single_page_app() -> None:
    """
    Input
        - None (this function runs the app with user interactions).
    Precondition
        - Streamlit is properly initialised and configured to run the app.
    Output
        - None (this function directly updates the UI).
    Postcondition
        - The main Streamlit app is fully functional, allowing users to input their preferences, retrieve weather data, and receive clothing suggestions.
    Invariant
        - The application’s layout and styling remain consistent across different user inputs and API responses.
    Side Effects
        - Interacts with external APIs, affecting network traffic and response times.
        - Updates the Streamlit session state with user inputs.
    """
    st.title('Weather 2 Wear')
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        <style>
            .weather-info {
                font-size: 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 10px 0;
            }
            .icon {
                font-size: 24px;
                margin-left: 10px;
            }
            .response-info {
                font-size: 24px;
                padding: 10px 0;
            }
        </style>
    """, unsafe_allow_html=True)

    st.header("Tell me about you!")
    st.write("Select your activity preferences and location (use a postcode or name)")

    activity_level = st.selectbox("Choose your activity level:", ["Low", "Medium", "High"])
    activity_type = st.selectbox("Choose your activity type:", ["Formal", "Informal", "Sport"])
    location = st.text_input("Enter your location:")

    if st.button("Submit"):
        if location:
            st.session_state.update({
                'activity_level': activity_level,
                'activity_type': activity_type,
                'location': location,
                'submitted': True
            })

            show_loading_bar("Fetching Weather Information")

            weather_url = f"https://qpfmxgvcalf556dxkuuwki3nri0drjzb.lambda-url.us-west-1.on.aws//?location={location}"
            weather_response = send_request(weather_url)

            if weather_response and weather_response.status_code == 200:
                try:
                    weather_data = weather_response.json()

                    if 'city' in weather_data:
                        city_name = weather_data['city']['name']
                        country_code = weather_data['city']['country']
                        st.success("Weather information retrieved successfully!")
                        st.subheader(f"Weather Information for {city_name}, {country_code}")

                    if 'list' in weather_data:
                        avg_temp, avg_humidity, avg_wind_speed, most_common_weather = process_weather_data(weather_data)
                        display_weather_summary(avg_temp, avg_humidity, avg_wind_speed, most_common_weather)

                        aggregated_data = {
                            "activity_level": activity_level.lower(),
                            "activity_type": activity_type.lower(),
                            "avg_temp": avg_temp,
                            "avg_humidity": avg_humidity,
                            "avg_wind_speed": avg_wind_speed,
                            "most_common_weather": most_common_weather
                        }

                        show_loading_bar("Generating Outfit Suggestions")

                        lambda_url = "https://igg7yuddu27z2bmtbroylfsarm0jxzrb.lambda-url.us-west-1.on.aws/"
                        lambda_response = send_request(lambda_url, method='POST', json_data=aggregated_data)

                        if lambda_response and lambda_response.status_code == 200:
                            st.subheader("AI Generated Clothing Recommendations")
                            suggestions = lambda_response.json()
                            formatted_suggestions = format_outfit_suggestions(suggestions)
                            st.markdown(f"<div class='response-info'>{formatted_suggestions}</div>",
                                        unsafe_allow_html=True)
                        else:
                            st.error(f"Failed to send data. Status code: {lambda_response.status_code}")
                            st.write("Response content:", lambda_response.text)

                        display_forecasts(weather_data['list'])

                except ValueError as e:
                    st.error("Failed to read weather data.")
                    st.write(e)
            else:
                st.error(f"Failed to fetch weather data. Status code: {weather_response.status_code}")
                st.write("Response content:", weather_response.text)
        else:
            st.error("Please enter a location.")


if __name__ == "__main__":
    st.set_page_config(page_title="Weather 2 Wear")
    single_page_app()

# Refactor Repetitive Code into Functions: Extract repeated code into functions to avoid redundancy and improve readability.
# Group Related Code into Classes or Functions: Organize related functionality into classes or separate functions. For example, weather data fetching and processing can be encapsulated into a separate function or class.
# Simplify State Management: Use Streamlit's session state more effectively to manage data across different interactions.
# Improve Error Handling and Logging: Centralize error handling and logging to make the code cleaner and easier to maintain.
# Key Changes:
# Modular Functions: Added functions for repetitive tasks (e.g., send_request, show_loading_bar, process_weather_data, display_weather_summary, display_forecasts).
# Error Handling: Centralized HTTP request error handling in send_request.
# State Management: Used st.session_state.update() to manage state updates more succinctly.
# Code Grouping: Grouped related operations into functions to improve cohesion and reduce coupling.
