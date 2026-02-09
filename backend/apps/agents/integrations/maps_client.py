"""
Maps and geocoding API integration client (Google Maps, Mapbox, etc.).
"""
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MapsClient:
    """
    Client for interacting with maps and geocoding APIs.
    """

    def __init__(self):
        """
        Initialize maps client with API credentials.
        """
        self.api_key = getattr(settings, 'MAPS_API_KEY', '')
        self.base_url = 'https://maps.googleapis.com/maps/api'
        self.timeout = 10
        self.cache_ttl = 86400  # Cache for 24 hours

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
            params['key'] = self.api_key

            url = f"{self.base_url}/{endpoint}/json"

            logger.debug(f"Making maps API request to {url}")

            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'OK':
                logger.warning(f"Maps API returned status: {data.get('status')}")
                return None

            return data

        except requests.exceptions.Timeout:
            logger.error("Maps API request timed out")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Maps API request failed: {str(e)}")
            return None

        except ValueError as e:
            logger.error(f"Failed to parse maps API response: {str(e)}")
            return None

    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to geographic coordinates.

        Args:
            address: Address string

        Returns:
            Location data or None
        """
        cache_key = f"maps:geocode:{address}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Returning cached geocoding data for: {address}")
            return cached_data

        try:
            logger.info(f"Geocoding address: {address}")

            params = {'address': address}

            data = self._make_request('geocode', params)

            if not data or not data.get('results'):
                return None

            result = data['results'][0]

            location_data = {
                'formatted_address': result['formatted_address'],
                'latitude': result['geometry']['location']['lat'],
                'longitude': result['geometry']['location']['lng'],
                'place_id': result['place_id'],
                'types': result['types'],
                'address_components': self._parse_address_components(result['address_components']),
                'viewport': result['geometry']['viewport'],
            }

            # Cache result
            cache.set(cache_key, location_data, self.cache_ttl)

            return location_data

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing geocoding data: {str(e)}")
            return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Convert coordinates to address.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Address data or None
        """
        cache_key = f"maps:reverse_geocode:{latitude}:{longitude}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Returning cached reverse geocoding data for: {latitude},{longitude}")
            return cached_data

        try:
            logger.info(f"Reverse geocoding coordinates: {latitude}, {longitude}")

            params = {'latlng': f"{latitude},{longitude}"}

            data = self._make_request('geocode', params)

            if not data or not data.get('results'):
                return None

            result = data['results'][0]

            address_data = {
                'formatted_address': result['formatted_address'],
                'place_id': result['place_id'],
                'types': result['types'],
                'address_components': self._parse_address_components(result['address_components']),
            }

            # Cache result
            cache.set(cache_key, address_data, self.cache_ttl)

            return address_data

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing reverse geocoding data: {str(e)}")
            return None

    def _parse_address_components(self, components: List[Dict]) -> Dict[str, str]:
        """
        Parse address components into a structured format.

        Args:
            components: Raw address components

        Returns:
            Parsed address components
        """
        parsed = {}

        type_mapping = {
            'street_number': 'street_number',
            'route': 'street',
            'locality': 'city',
            'administrative_area_level_1': 'state',
            'administrative_area_level_2': 'county',
            'country': 'country',
            'postal_code': 'postal_code',
        }

        for component in components:
            for comp_type in component['types']:
                if comp_type in type_mapping:
                    key = type_mapping[comp_type]
                    parsed[key] = component['long_name']

                    if comp_type == 'country':
                        parsed['country_code'] = component['short_name']

                    if comp_type == 'administrative_area_level_1':
                        parsed['state_code'] = component['short_name']

        return parsed

    def get_distance(self, origin: Tuple[float, float], destination: Tuple[float, float],
                    mode: str = 'driving') -> Optional[Dict[str, Any]]:
        """
        Calculate distance and duration between two points.

        Args:
            origin: Origin coordinates (lat, lng)
            destination: Destination coordinates (lat, lng)
            mode: Travel mode ('driving', 'walking', 'bicycling', 'transit')

        Returns:
            Distance and duration data or None
        """
        try:
            logger.info(f"Calculating distance from {origin} to {destination}")

            origin_str = f"{origin[0]},{origin[1]}"
            destination_str = f"{destination[0]},{destination[1]}"

            params = {
                'origins': origin_str,
                'destinations': destination_str,
                'mode': mode,
                'units': 'metric'
            }

            data = self._make_request('distancematrix', params)

            if not data or not data.get('rows'):
                return None

            element = data['rows'][0]['elements'][0]

            if element['status'] != 'OK':
                logger.warning(f"Distance matrix returned status: {element['status']}")
                return None

            return {
                'distance_meters': element['distance']['value'],
                'distance_text': element['distance']['text'],
                'duration_seconds': element['duration']['value'],
                'duration_text': element['duration']['text'],
                'mode': mode,
            }

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing distance data: {str(e)}")
            return None

    def get_directions(self, origin: Tuple[float, float], destination: Tuple[float, float],
                      mode: str = 'driving', waypoints: List[Tuple[float, float]] = None) -> Optional[Dict[str, Any]]:
        """
        Get directions between two points.

        Args:
            origin: Origin coordinates (lat, lng)
            destination: Destination coordinates (lat, lng)
            mode: Travel mode
            waypoints: Optional list of waypoint coordinates

        Returns:
            Directions data or None
        """
        try:
            logger.info(f"Getting directions from {origin} to {destination}")

            origin_str = f"{origin[0]},{origin[1]}"
            destination_str = f"{destination[0]},{destination[1]}"

            params = {
                'origin': origin_str,
                'destination': destination_str,
                'mode': mode,
            }

            if waypoints:
                waypoints_str = '|'.join([f"{wp[0]},{wp[1]}" for wp in waypoints])
                params['waypoints'] = waypoints_str

            data = self._make_request('directions', params)

            if not data or not data.get('routes'):
                return None

            route = data['routes'][0]
            leg = route['legs'][0]

            directions = {
                'distance_meters': leg['distance']['value'],
                'distance_text': leg['distance']['text'],
                'duration_seconds': leg['duration']['value'],
                'duration_text': leg['duration']['text'],
                'start_address': leg['start_address'],
                'end_address': leg['end_address'],
                'start_location': leg['start_location'],
                'end_location': leg['end_location'],
                'steps': [],
                'polyline': route['overview_polyline']['points'],
                'bounds': route['bounds'],
            }

            # Parse steps
            for step in leg['steps']:
                directions['steps'].append({
                    'distance': step['distance']['text'],
                    'duration': step['duration']['text'],
                    'instruction': step['html_instructions'],
                    'start_location': step['start_location'],
                    'end_location': step['end_location'],
                    'travel_mode': step['travel_mode'],
                })

            return directions

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing directions data: {str(e)}")
            return None

    def search_nearby(self, latitude: float, longitude: float, place_type: str,
                     radius: int = 5000, keyword: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        Search for nearby places.

        Args:
            latitude: Latitude
            longitude: Longitude
            place_type: Type of place (restaurant, hotel, tourist_attraction, etc.)
            radius: Search radius in meters (max 50000)
            keyword: Optional search keyword

        Returns:
            List of places or None
        """
        cache_key = f"maps:nearby:{latitude}:{longitude}:{place_type}:{radius}:{keyword}"
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.debug(f"Returning cached nearby search data")
            return cached_data

        try:
            logger.info(f"Searching nearby places: {place_type} near {latitude}, {longitude}")

            params = {
                'location': f"{latitude},{longitude}",
                'radius': min(radius, 50000),  # Max 50km
                'type': place_type,
            }

            if keyword:
                params['keyword'] = keyword

            data = self._make_request('place/nearbysearch', params)

            if not data or not data.get('results'):
                return []

            places = []

            for result in data['results']:
                places.append({
                    'place_id': result['place_id'],
                    'name': result['name'],
                    'address': result.get('vicinity', ''),
                    'latitude': result['geometry']['location']['lat'],
                    'longitude': result['geometry']['location']['lng'],
                    'rating': result.get('rating'),
                    'user_ratings_total': result.get('user_ratings_total'),
                    'price_level': result.get('price_level'),
                    'types': result['types'],
                    'open_now': result.get('opening_hours', {}).get('open_now'),
                    'photos': [photo['photo_reference'] for photo in result.get('photos', [])[:3]],
                })

            # Cache result
            cache.set(cache_key, places, self.cache_ttl // 2)  # Cache for 12 hours

            return places

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing nearby search data: {str(e)}")
            return None

    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a place.

        Args:
            place_id: Google Place ID

        Returns:
            Place details or None
        """
        cache_key = f"maps:place_details:{place_id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            logger.info(f"Getting place details for: {place_id}")

            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,opening_hours,website,rating,reviews,photos,geometry,types,price_level'
            }

            data = self._make_request('place/details', params)

            if not data or not data.get('result'):
                return None

            result = data['result']

            place_details = {
                'place_id': place_id,
                'name': result['name'],
                'address': result.get('formatted_address'),
                'phone': result.get('formatted_phone_number'),
                'website': result.get('website'),
                'latitude': result['geometry']['location']['lat'],
                'longitude': result['geometry']['location']['lng'],
                'rating': result.get('rating'),
                'types': result['types'],
                'price_level': result.get('price_level'),
                'opening_hours': result.get('opening_hours'),
                'reviews': result.get('reviews', [])[:5],  # Top 5 reviews
                'photos': [photo['photo_reference'] for photo in result.get('photos', [])[:5]],
            }

            # Cache result
            cache.set(cache_key, place_details, self.cache_ttl)

            return place_details

        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing place details: {str(e)}")
            return None

    def optimize_route(self, waypoints: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Optimize route order for multiple waypoints.

        Args:
            waypoints: List of waypoint dictionaries with 'lat', 'lng', 'id' keys

        Returns:
            Optimized route data or None
        """
        try:
            if len(waypoints) < 2:
                return {'order': [wp['id'] for wp in waypoints]}

            logger.info(f"Optimizing route for {len(waypoints)} waypoints")

            # For now, use a simple greedy nearest neighbor algorithm
            # In production, you would use Google Directions API with waypoint optimization

            unvisited = waypoints.copy()
            route = []
            current = unvisited.pop(0)
            route.append(current['id'])

            total_distance = 0
            total_duration = 0

            while unvisited:
                # Find nearest unvisited waypoint
                nearest = None
                min_distance = float('inf')

                for wp in unvisited:
                    distance_data = self.get_distance(
                        (current['lat'], current['lng']),
                        (wp['lat'], wp['lng'])
                    )

                    if distance_data and distance_data['distance_meters'] < min_distance:
                        min_distance = distance_data['distance_meters']
                        nearest = wp

                if nearest:
                    route.append(nearest['id'])
                    total_distance += min_distance

                    # Get duration for this segment
                    distance_data = self.get_distance(
                        (current['lat'], current['lng']),
                        (nearest['lat'], nearest['lng'])
                    )
                    if distance_data:
                        total_duration += distance_data['duration_seconds']

                    unvisited.remove(nearest)
                    current = nearest
                else:
                    # Couldn't find nearest, just add remaining
                    route.extend([wp['id'] for wp in unvisited])
                    break

            return {
                'order': route,
                'total_distance': total_distance,
                'total_duration': total_duration,
            }

        except Exception as e:
            logger.error(f"Error optimizing route: {str(e)}")
            return None

    def get_timezone(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get timezone for coordinates.

        Args:
            latitude: Latitude
            longitude: Longitude

        Returns:
            Timezone name or None
        """
        cache_key = f"maps:timezone:{latitude}:{longitude}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            import time

            logger.info(f"Getting timezone for coordinates: {latitude}, {longitude}")

            params = {
                'location': f"{latitude},{longitude}",
                'timestamp': int(time.time())
            }

            data = self._make_request('timezone', params)

            if not data:
                return None

            timezone_id = data['timeZoneId']

            # Cache result (timezones don't change)
            cache.set(cache_key, timezone_id, self.cache_ttl * 7)  # Cache for 1 week

            return timezone_id

        except (KeyError, TypeError) as e:
            logger.error(f"Error getting timezone: {str(e)}")
            return None
