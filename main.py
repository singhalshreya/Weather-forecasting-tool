import requests
import json
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from geopy.geocoders import Nominatim
from azure.storage.blob import BlobServiceClient

load_dotenv()


def get_weather_forecast(api_key, city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature_kelvin = data['main']['temp']
        temperature_celsius = temperature_kelvin - 273.15
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        print(f"Weather forecast for {city}:")
        print(f"Weather: {weather}")
        print(f"Temperature: {temperature_celsius:.2f} °C")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s")

        # Perform sentiment analysis using Azure Cognitive Services Text Analytics
        text = f"Weather forecast for {city}: {weather}"
        perform_sentiment_analysis(text)

        # Retrieve location coordinates using Azure Maps
        location = city
        coordinates = retrieve_location_coordinates(location)
        print(f"Coordinates for {location}: Latitude={coordinates[0]}, Longitude={coordinates[1]}")

        # Display weather forecast on a map using Azure Maps
        display_weather_on_map(coordinates, weather)

        # Store weather data in Azure Blob Storage
        store_weather_data(city, data)

        # Perform historical weather data analysis
        historical_data = get_historical_weather_data(city)
        analyze_historical_data(historical_data)
    else:
        print("Unable to fetch weather data. Please try again.")

def perform_sentiment_analysis(text):
    text_analytics_key = os.getenv("TEXT_ANALYTICS_KEY")
    text_analytics_endpoint = os.getenv("TEXT_ANALYTICS_ENDPOINT")

    credential = AzureKeyCredential(text_analytics_key)
    client = TextAnalyticsClient(endpoint=text_analytics_endpoint, credential=credential)

    response = client.analyze_sentiment([text])
    sentiment_score = response[0].confidence_scores
    print(f"Sentiment scores: Positive={sentiment_score.positive:.2f}, Negative={sentiment_score.negative:.2f}, Neutral={sentiment_score.neutral:.2f}")


def retrieve_location_coordinates(location):
    geolocator = Nominatim(user_agent="weather-forecast")
    location_data = geolocator.geocode(location)
    coordinates = (location_data.latitude, location_data.longitude)
    return coordinates

def display_weather_on_map(coordinates, weather):
    maps_subscription_key = os.getenv("AZURE_MAPS_SUBSCRIPTION_KEY")

    map_url = f"https://atlas.microsoft.com/map/static/png?subscription-key={maps_subscription_key}&api-version=1.0&center={coordinates[0]},{coordinates[1]}&zoom=12&layer=basic&height=500&width=800"
    print("Weather forecast map:")
    print(map_url)

def store_weather_data(city, data):
    blob_connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    container_name = "polaroid4"

    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_name = f"{city}.json"
    blob_client = container_client.get_blob_client(blob_name)

    data_bytes = json.dumps(data).encode('utf-8')
    blob_client.upload_blob(data_bytes, overwrite=True)

def get_historical_weather_data(city):
    # Retrieve historical weather data
    historical_data = {}  # Placeholder for historical weather data retrieval logic
    return historical_data

def analyze_historical_data(historical_data):
    # Process and analyze historical weather data
    # Example code for analysis and visualization
    df = pd.DataFrame.from_dict(historical_data)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Calculate statistics
    mean_temperature = df['temperature'].mean()
    max_temperature = df['temperature'].max()
    min_temperature = df['temperature'].min()

    # Plot temperature over time
    plt.plot(df.index, df['temperature'])
    plt.title('Historical Temperature')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.show()

    print("Historical Weather Data Analysis:")
    print(f"Mean Temperature: {mean_temperature} °C")
    print(f"Max Temperature: {max_temperature} °C")
    print(f"Min Temperature: {min_temperature} °C")

if __name__ == '__main__':
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    city = input("Enter the city name: ")

    get_weather_forecast(api_key, city)
