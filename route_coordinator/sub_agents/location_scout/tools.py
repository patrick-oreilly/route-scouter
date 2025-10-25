import requests
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import Dict, List
from config import settings

def geocode_location(location_name: str) -> Dict:
    """
    Convert location name to coordinates.

    Args:
        location_name: Name of the location to geocode

    Returns:
        dict: Contains lat/lng coordinates and formatted address
    """
    start_time = time.time()

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": settings.google_maps_api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        duration_ms = int((time.time() - start_time) * 1000)

        if data['status'] == 'OK':
            result = data['results'][0]


            return {
                "status": "success",
                "latitude": result['geometry']['location']['lat'],
                "longitude": result['geometry']['location']['lng'],
                "formatted_address": result['formatted_address'],
                "place_id": result.get('place_id')
            }
        else:
            return {
                "status": "error",
                "error_message": f"Geocoding failed: {data['status']}"
            }

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "error",
            "error_message": str(e)
        }


def find_nearby_places(
    lat: float,
    lng: float,
    place_type: str,
    radius: int,
) -> Dict:
    """
    Find places near a location (trailheads, parking, amenities).

    Args:
        lat: Latitude
        lng: Longitude
        place_type: Type of place (e.g., 'parking', 'campground', 'restaurant')
        radius: Search radius in meters

    Returns:
        dict: List of nearby places with details
    """
    start_time = time.time()

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "key": settings.google_maps_api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        duration_ms = int((time.time() - start_time) * 1000)

        if data['status'] == 'OK':
            places = [
                {
                    "name": place['name'],
                    "address": place.get('vicinity', 'N/A'),
                    "rating": place.get('rating', 'N/A'),
                    "latitude": place['geometry']['location']['lat'],
                    "longitude": place['geometry']['location']['lng']
                }
                for place in data['results'][:5]  # Top 5 results
            ]

            return {
                "status": "success",
                "places": places,
                "count": len(places)
            }
        else:

            return {
                "status": "error",
                "error_message": f"Places API returned: {data['status']}"
            }

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
     
        return {
            "status": "error",
            "error_message": str(e)
        }