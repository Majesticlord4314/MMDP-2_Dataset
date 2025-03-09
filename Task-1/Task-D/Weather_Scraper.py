import requests
import csv
import time
from datetime import datetime

# List of 20 Indian cities
cities = [
    "Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Nagpur", "Indore", "Bhopal", "Coimbatore", "Visakhapatnam",
    "Surat", "Vijayawada", "Kanpur", "Agra", "Varanasi"
]

# WeatherAPI.com key and endpoint
api_key = "84da75c3a5d14fdf82c103434250803"
base_url = "http://api.weatherapi.com/v1/current.json"

# CSV file to store weather data
csv_filename = "Indian_Weather_Trend.csv"

# Write header if file doesn't exist
try:
    with open(csv_filename, 'x', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Timestamp", "City", "Temperature (°C)", "Humidity (%)", "Wind Speed (kph)"])
except FileExistsError:
    # File already exists; data will be appended.
    pass

# For demo purposes, we run a few iterations.
# In production, schedule this script (e.g., via cron) to run periodically (hourly, daily, etc.)
num_iterations = 2  
delay_seconds = 10  # Adjust this delay as needed (e.g., 3600 for hourly data collection)

for i in range(num_iterations):
    print(f"\nIteration {i+1} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for city in cities:
            params = {
                "key": api_key,
                "q": city,
                "aqi": "no"
            }
            try:
                response = requests.get(base_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    temperature = data["current"]["temp_c"]
                    humidity = data["current"]["humidity"]
                    wind_speed = data["current"]["wind_kph"]
                    writer.writerow([timestamp, city, temperature, humidity, wind_speed])
                    print(f"  {city}: Temp={temperature}°C, Humidity={humidity}%, Wind={wind_speed} kph")
                else:
                    print(f"  Error fetching data for {city}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  Exception for {city}: {e}")
    print(f"Waiting {delay_seconds} seconds before next iteration...\n")
    time.sleep(delay_seconds)

print("Data collection completed. Weather data stored in", csv_filename)
