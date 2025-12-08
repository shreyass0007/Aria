import os
import requests
import json
import time
from .config import settings

class WeatherManager:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self._cache = {}
        self._cache_expiry = 600  # 10 minutes in seconds

    def _get_weather_advice(self, weather_desc: str, temp: float) -> str:
        """
        Generate friendly, conversational advice based on weather conditions.
        """
        import random
        
        advice = []
        weather_lower = weather_desc.lower()
        
        # Rain-related advice (friendly variations)
        if any(word in weather_lower for word in ['rain', 'drizzle', 'shower']):
            rain_advice = [
                "Don't forget your umbrella, you'll need it!",
                "Grab an umbrella before heading out!",
                "It's gonna rain, better take that umbrella with you!",
                "Pack an umbrella, looks like it's going to pour!",
                "Rain's expected, so don't leave without your umbrella!"
            ]
            advice.append(random.choice(rain_advice))
        
        # Sun/Clear weather advice (friendly variations)
        if any(word in weather_lower for word in ['clear', 'sunny']):
            if temp > 25:
                sunny_hot_advice = [
                    "It's pretty sunny out there! Slap on some sunscreen before you go.",
                    "Don't forget the sunscreen today, it's really sunny!",
                    "Sunshine alert! Better put on some sunscreen.",
                    "Grab your sunglasses and sunscreen, it's going to be bright!",
                    "It's a scorcher! Make sure to apply sunscreen."
                ]
                advice.append(random.choice(sunny_hot_advice))
            else:
                sunny_nice_advice = [
                    "Perfect weather for a walk! Enjoy it!",
                    "What a beautiful day! Great time to go outside!",
                    "It's gorgeous out there, perfect for some outdoor fun!",
                    "Lovely weather today! Maybe grab a coffee outside?",
                    "Beautiful clear skies! Perfect day to enjoy the outdoors!"
                ]
                advice.append(random.choice(sunny_nice_advice))
        
        # Cloud/Overcast advice (friendly variations)
        if any(word in weather_lower for word in ['cloud', 'overcast']):
            cloudy_advice = [
                "A bit cloudy today. Maybe grab a light jacket just in case!",
                "It's looking a bit gray out there, bring a jacket!",
                "Cloudy skies ahead, might want to layer up a bit.",
                "Overcast today, so maybe carry a light jacket with you.",
                "Clouds are rolling in, better take something warm!"
            ]
            advice.append(random.choice(cloudy_advice))
        
        # Storm/Thunder advice (friendly but serious)
        if any(word in weather_lower for word in ['storm', 'thunder']):
            storm_advice = [
                "Whoa, there's a storm brewing! Better stay inside if you can.",
                "Looks like some serious weather. Stay safe and indoors!",
                "Thunderstorms expected! Maybe postpone that outdoor plan?",
                "Storm's coming! Best to stay cozy indoors today.",
                "Severe weather alert! Stay inside and stay safe, okay?"
            ]
            advice.append(random.choice(storm_advice))
        
        # Snow advice (friendly variations)
        if 'snow' in weather_lower:
            snow_advice = [
                "It's snowing! Bundle up warm and drive super carefully!",
                "Snow day! Dress warmly and watch out on the roads!",
                "Snowy weather ahead! Layer up and be careful out there!",
                "Time to break out the winter coat! It's snowing!",
                "Snow's falling! Stay warm and drive safely!"
            ]
            advice.append(random.choice(snow_advice))
        
        # Fog/Mist advice (friendly variations)
        if any(word in weather_lower for word in ['fog', 'mist', 'haze']):
            fog_advice = [
                "It's pretty foggy out there. Drive carefully, okay?",
                "Visibility's not great with all this fog. Take it slow!",
                "Misty conditions today, so be extra careful on the road!",
                "Foggy weather! Can't see much, so drive safe!",
                "Quite hazy today. Keep your headlights on and drive carefully!"
            ]
            advice.append(random.choice(fog_advice))
        
        # Temperature-based advice (friendly variations)
        if temp < 10:
            cold_advice = [
                "Brrr, it's cold! Make sure you wear something warm!",
                "It's freezing out there! Layer up before you go!",
                "Pretty chilly today! Don't forget your jacket!",
                "Wear something cozy, it's quite cold!",
                "Bundle up! It's cold enough to see your breath!"
            ]
            advice.append(random.choice(cold_advice))
        elif temp > 35:
            hot_advice = [
                "Whoa, it's really hot! Stay hydrated and avoid the sun when you can!",
                "It's a scorcher today! Drink lots of water and stay in the shade!",
                "Super hot outside! Keep a water bottle handy and take it easy!",
                "It's blazing hot! Stay cool and hydrated, friend!",
                "Heat wave alert! Take breaks in the AC and drink plenty of water!"
            ]
            advice.append(random.choice(hot_advice))
        
        return " ".join(advice) if advice else ""

    def get_weather(self, city_name: str) -> str:
        """
        Fetches weather for a given city.
        Returns a human-readable string with contextual advice.
        """
        if not self.api_key:
            return "I cannot check the weather because the OpenWeather API key is missing."

        if not city_name:
            return "Please specify a city name."

        # Check Cache
        current_time = time.time()
        if city_name in self._cache:
            cached_data, timestamp = self._cache[city_name]
            if current_time - timestamp < self._cache_expiry:
                # print(f"DEBUG: Returning cached weather for {city_name}")
                return cached_data

        try:
            params = {
                "q": city_name,
                "appid": self.api_key,
                "units": "metric"  # Use metric units (Celsius)
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()

            if response.status_code == 200:
                weather_desc = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                
                # Build base weather message
                base_msg = f"The weather in {city_name} is currently {weather_desc} with a temperature of {temp} degrees Celsius. It feels like {feels_like} degrees, and the humidity is {humidity}%."
                
                # Get contextual advice
                advice = self._get_weather_advice(weather_desc, temp)
                
                # Combine message with advice
                if advice:
                    result = f"{base_msg} {advice}"
                else:
                    result = base_msg
                
                # Update Cache
                self._cache[city_name] = (result, current_time)
                return result
                    
            elif response.status_code == 404:
                return f"I couldn't find weather information for {city_name}. Please check the city name."
            else:
                return f"Sorry, I encountered an error checking the weather: {data.get('message', 'Unknown error')}"

        except Exception as e:
            print(f"Weather API Error: {e}")
            return "Sorry, I'm having trouble connecting to the weather service right now."

    def get_weather_summary(self) -> str:
        """
        Returns a summary of the weather for the default city.
        Used for morning briefings.
        """
        return self.get_weather(settings.DEFAULT_CITY)
