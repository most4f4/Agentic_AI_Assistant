"""
Weather tool for getting current weather information
"""
import os
import requests
from langchain.tools import tool
from langchain.pydantic_v1 import BaseModel, Field


class WeatherInput(BaseModel):
    city: str = Field(description="The name of the city to get weather for")


@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """Get current weather information for any city in the world.
    Returns temperature, conditions, humidity, and wind speed."""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "OpenWeatherMap API key not configured. Please add OPENWEATHER_API_KEY to your .env file"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather_desc = data['weather'][0]['description'].title()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            return f"Weather in {city}:\n- Temperature: {temp}°C (feels like {feels_like}°C)\n- Condition: {weather_desc}\n- Humidity: {humidity}%\n- Wind Speed: {wind_speed} m/s"
        else:
            return f"Could not find weather data for {city}. Please check the city name."
    except Exception as e:
        return f"Failed to get weather data: {e}"