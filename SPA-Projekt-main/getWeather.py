from dataclasses import dataclass
import requests

BASE_URL = "https://api.weatherapi.com/v1/current.json"

@dataclass
class Weather:
    city: str
    country: str
    temp_c: float
    condition: str
    humidity: int
    wind_kph: float

def get_weather(api_key: str, city: str) -> Weather:
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no",
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return Weather(
        city=data["location"]["name"],
        country=data["location"]["country"],
        temp_c=data["current"]["temp_c"],
        condition=data["current"]["condition"]["text"],
        humidity=data["current"]["humidity"],
        wind_kph=data["current"]["wind_kph"],
    )