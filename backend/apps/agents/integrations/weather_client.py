"""
Weather API integration client.
"""
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class WeatherClient:
    """
    Client for interacting with weather API (OpenWeatherMap, WeatherAPI, etc.).
    """

    def __init__(self):
        """
        Initialize weather client with API credentials.
        """
        self.api_key = getattr(settings, 'WEATHER_API_KEY', '')
        self.base_url = getattr(settings, 'WEATHER_API_BASE_URL', 'https://api.openweathermap.org/data/2.5')
        self.timeout = 10  # Request timeout in seconds
        self.cache_ttl = 3600  # Cache for 1 hour

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """
        Make API request with error handling.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data or None
        """
        try:
            params['appid'] = self.api_key

            url = f"{self.base_url}/{endpoint}"

            logger.debug(f"Making weather API request to {url}")

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Weather API request timed out")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {str(e)}")
            return None

        except ValueError as e:
            logger.error(f"Failed to parse weather API response: {str(e)}")
            return None

    def get_current_weather(self, latitude: float, longitude: float, units: str = 'metric') -> Optional[Dict[str, Any]]:
        """
        Get current weather for coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude
            units: Units system ('metric', 'imperial', 'standard')

        Returns:
            Weather data or None
        """
        # Check cache first
        cache_key = f"weather:current:{latitude}:{longitude}:{units}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Returning cached weather data for {latitude},{longitude}")
            return cached_data

        try:
            logger.info(f"Fetching current weather for coordinates: {latitude}, {longitude}")

            params = {
                'lat': latitude,
                'lon': longitude,
                'units': units
            }

            data = self._make_request('weather', params)

            if not data:
                return None

            # Parse response
            weather = {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity'],
                'condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg'),
                'clouds': data['clouds']['all'],
                'visibility': data.get('visibility'),
                'timestamp': datetime.fromtimestamp(data['dt']),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'location': data['name'],
            }

            # Cache result
            cache.set(cache_key, weather, self.cache_ttl)

            return weather

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing weather data: {str(e)}")
            return None

    def get_forecast(self, latitude: float, longitude: float, date: datetime = None,
                     units: str = 'metric') -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude
            date: Optional specific date to get forecast for
            units: Units system ('metric', 'imperial', 'standard')

        Returns:
            Forecast data or None
        """
        # Check cache first
        date_str = date.strftime('%Y-%m-%d') if date else 'all'
        cache_key = f"weather:forecast:{latitude}:{longitude}:{date_str}:{units}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Returning cached forecast data for {latitude},{longitude}")
            return cached_data

        try:
            logger.info(f"Fetching weather forecast for coordinates: {latitude}, {longitude}")

            params = {
                'lat': latitude,
                'lon': longitude,
                'units': units,
                'cnt': 40  # 5 days, 3-hour intervals
            }

            data = self._make_request('forecast', params)

            if not data:
                return None

            # If specific date requested, find matching forecast
            if date:
                target_date = date.date()

                for item in data['list']:
                    forecast_date = datetime.fromtimestamp(item['dt']).date()

                    if forecast_date == target_date:
                        forecast = {
                            'date': forecast_date,
                            'temp_high': item['main']['temp_max'],
                            'temp_low': item['main']['temp_min'],
                            'temperature': item['main']['temp'],
                            'feels_like': item['main']['feels_like'],
                            'condition': item['weather'][0]['main'],
                            'description': item['weather'][0]['description'],
                            'icon': item['weather'][0]['icon'],
                            'precipitation_probability': item.get('pop', 0) * 100,
                            'humidity': item['main']['humidity'],
                            'wind_speed': item['wind']['speed'],
                            'clouds': item['clouds']['all'],
                        }

                        # Cache result
                        cache.set(cache_key, forecast, self.cache_ttl)

                        return forecast

                return None

            # Return full forecast
            forecast_data = []

            for item in data['list']:
                forecast_data.append({
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'condition': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'precipitation_probability': item.get('pop', 0) * 100,
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                })

            result = {
                'location': data['city']['name'],
                'forecasts': forecast_data
            }

            # Cache result
            cache.set(cache_key, result, self.cache_ttl)

            return result

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing forecast data: {str(e)}")
            return None

    def get_daily_forecast(self, latitude: float, longitude: float, days: int = 7,
                          units: str = 'metric') -> Optional[List[Dict[str, Any]]]:
        """
        Get daily weather forecast.

        Args:
            latitude: Latitude
            longitude: Longitude
            days: Number of days to forecast (max 7 for free tier)
            units: Units system

        Returns:
            List of daily forecasts or None
        """
        cache_key = f"weather:daily:{latitude}:{longitude}:{days}:{units}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            logger.info(f"Fetching {days}-day forecast for coordinates: {latitude}, {longitude}")

            # Using One Call API for daily forecast
            params = {
                'lat': latitude,
                'lon': longitude,
                'exclude': 'current,minutely,hourly,alerts',
                'units': units,
                'cnt': days
            }

            data = self._make_request('onecall', params)

            if not data or 'daily' not in data:
                return None

            daily_forecasts = []

            for day_data in data['daily'][:days]:
                daily_forecasts.append({
                    'date': datetime.fromtimestamp(day_data['dt']).date(),
                    'temp_high': day_data['temp']['max'],
                    'temp_low': day_data['temp']['min'],
                    'temp_morning': day_data['temp']['morn'],
                    'temp_day': day_data['temp']['day'],
                    'temp_evening': day_data['temp']['eve'],
                    'temp_night': day_data['temp']['night'],
                    'feels_like_day': day_data['feels_like']['day'],
                    'condition': day_data['weather'][0]['main'],
                    'description': day_data['weather'][0]['description'],
                    'icon': day_data['weather'][0]['icon'],
                    'precipitation_probability': day_data.get('pop', 0) * 100,
                    'rain': day_data.get('rain', 0),
                    'snow': day_data.get('snow', 0),
                    'humidity': day_data['humidity'],
                    'wind_speed': day_data['wind_speed'],
                    'wind_direction': day_data.get('wind_deg'),
                    'clouds': day_data['clouds'],
                    'uv_index': day_data.get('uvi', 0),
                    'sunrise': datetime.fromtimestamp(day_data['sunrise']),
                    'sunset': datetime.fromtimestamp(day_data['sunset']),
                })

            # Cache result
            cache.set(cache_key, daily_forecasts, self.cache_ttl)

            return daily_forecasts

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing daily forecast data: {str(e)}")
            return None

    def get_weather_by_city(self, city_name: str, country_code: str = None,
                           units: str = 'metric') -> Optional[Dict[str, Any]]:
        """
        Get current weather by city name.

        Args:
            city_name: City name
            country_code: Optional ISO 3166 country code
            units: Units system

        Returns:
            Weather data or None
        """
        cache_key = f"weather:city:{city_name}:{country_code}:{units}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            logger.info(f"Fetching weather for city: {city_name}")

            query = city_name
            if country_code:
                query = f"{city_name},{country_code}"

            params = {
                'q': query,
                'units': units
            }

            data = self._make_request('weather', params)

            if not data:
                return None

            weather = {
                'city': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'latitude': data['coord']['lat'],
                    'longitude': data['coord']['lon']
                },
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'timestamp': datetime.fromtimestamp(data['dt']),
            }

            # Cache result
            cache.set(cache_key, weather, self.cache_ttl)

            return weather

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing weather data: {str(e)}")
            return None

    def get_weather_alerts(self, latitude: float, longitude: float) -> Optional[List[Dict[str, Any]]]:
        """
        Get weather alerts for location.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            List of weather alerts or None
        """
        try:
            logger.info(f"Fetching weather alerts for coordinates: {latitude}, {longitude}")

            params = {
                'lat': latitude,
                'lon': longitude,
                'exclude': 'current,minutely,hourly,daily'
            }

            data = self._make_request('onecall', params)

            if not data or 'alerts' not in data:
                return []

            alerts = []

            for alert in data['alerts']:
                alerts.append({
                    'event': alert['event'],
                    'start': datetime.fromtimestamp(alert['start']),
                    'end': datetime.fromtimestamp(alert['end']),
                    'description': alert['description'],
                    'sender': alert.get('sender_name', 'Unknown'),
                })

            return alerts

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing alerts data: {str(e)}")
            return None

    def get_air_quality(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get air quality index for location.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Air quality data or None
        """
        cache_key = f"weather:aqi:{latitude}:{longitude}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            logger.info(f"Fetching air quality for coordinates: {latitude}, {longitude}")

            params = {
                'lat': latitude,
                'lon': longitude
            }

            data = self._make_request('air_pollution', params)

            if not data:
                return None

            aqi_data = data['list'][0]

            air_quality = {
                'aqi': aqi_data['main']['aqi'],  # 1-5 scale
                'co': aqi_data['components']['co'],
                'no': aqi_data['components']['no'],
                'no2': aqi_data['components']['no2'],
                'o3': aqi_data['components']['o3'],
                'so2': aqi_data['components']['so2'],
                'pm2_5': aqi_data['components']['pm2_5'],
                'pm10': aqi_data['components']['pm10'],
                'nh3': aqi_data['components']['nh3'],
                'timestamp': datetime.fromtimestamp(aqi_data['dt']),
            }

            # Add quality description
            aqi_descriptions = {
                1: 'Good',
                2: 'Fair',
                3: 'Moderate',
                4: 'Poor',
                5: 'Very Poor'
            }
            air_quality['description'] = aqi_descriptions.get(air_quality['aqi'], 'Unknown')

            # Cache result
            cache.set(cache_key, air_quality, self.cache_ttl)

            return air_quality

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing air quality data: {str(e)}")
            return None
