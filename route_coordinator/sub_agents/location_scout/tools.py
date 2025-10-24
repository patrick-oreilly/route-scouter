import requests
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import Dict, List
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

def geocode_location(location_name: str) -> Dict:
    """
    Convert location name to coordinates.

    Args:
        location_name: Name of the location to geocode

    Returns:
        dict: Contains lat/lng coordinates and formatted address
    """
    start_time = time.time()

    logger.info(
        "Geocoding location",
        extra={
            "agent_name": "location_scout",
            "location_name": location_name
        }
    )

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": settings.google_maps_api_key
    }

    try:
        logger.debug("Calling Google Geocoding API")
        response = requests.get(url, params=params)
        data = response.json()

        duration_ms = int((time.time() - start_time) * 1000)

        if data['status'] == 'OK':
            result = data['results'][0]

            logger.info(
                "Location geocoded successfully",
                extra={
                    "agent_name": "location_scout",
                    "duration_ms": duration_ms,
                    "formatted_address": result['formatted_address']
                }
            )

            return {
                "status": "success",
                "latitude": result['geometry']['location']['lat'],
                "longitude": result['geometry']['location']['lng'],
                "formatted_address": result['formatted_address'],
                "place_id": result.get('place_id')
            }
        else:
            logger.warning(
                f"Geocoding failed: {data['status']}",
                extra={
                    "agent_name": "location_scout",
                    "duration_ms": duration_ms,
                    "api_status": data['status'],
                    "location_name": location_name
                }
            )
            return {
                "status": "error",
                "error_message": f"Geocoding failed: {data['status']}"
            }

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"Error geocoding location: {str(e)}",
            exc_info=True,
            extra={
                "agent_name": "location_scout",
                "duration_ms": duration_ms,
                "error_type": type(e).__name__,
                "location_name": location_name
            }
        )
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

    logger.info(
        "Finding nearby places",
        extra={
            "agent_name": "location_scout",
            "place_type": place_type,
            "radius": radius,
            "lat": lat,
            "lng": lng
        }
    )

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": place_type,
        "key": settings.google_maps_api_key
    }

    try:
        logger.debug("Calling Google Places API")
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

            logger.info(
                "Nearby places found",
                extra={
                    "agent_name": "location_scout",
                    "duration_ms": duration_ms,
                    "place_type": place_type,
                    "places_found": len(places)
                }
            )

            return {
                "status": "success",
                "places": places,
                "count": len(places)
            }
        else:
            logger.warning(
                f"Places API error: {data['status']}",
                extra={
                    "agent_name": "location_scout",
                    "duration_ms": duration_ms,
                    "api_status": data['status'],
                    "place_type": place_type
                }
            )
            return {
                "status": "error",
                "error_message": f"Places API returned: {data['status']}"
            }

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"Error finding nearby places: {str(e)}",
            exc_info=True,
            extra={
                "agent_name": "location_scout",
                "duration_ms": duration_ms,
                "error_type": type(e).__name__,
                "place_type": place_type
            }
        )
        return {
            "status": "error",
            "error_message": str(e)
        }