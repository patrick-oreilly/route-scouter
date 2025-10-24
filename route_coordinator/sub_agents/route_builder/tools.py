import requests
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from typing import Dict, List, Optional
from urllib.parse import quote
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

def get_running_directions(
    origin: str,
    destination: str,
    waypoints: List[str] = None,
    avoid_highways: bool = True,
) -> Dict:
    """
    Get running directions between locations.

    Args:
        origin: Starting location
        destination: Ending location
        waypoints: Optional list of intermediate points
        avoid_highways: Avoid major highways (default True for safety)

    Returns:
        dict: Route information optimized for runners
    """
    start_time = time.time()

    logger.info(
        "Getting running directions",
        extra={
            "agent_name": "route_builder",
            "origin": origin,
            "destination": destination,
            "waypoint_count": len(waypoints) if waypoints else 0,
            "avoid_highways": avoid_highways
        }
    )

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "mode": "walking",  # Walking mode for runners
        "key": settings.google_maps_api_key
    }

    if waypoints:
        params["waypoints"] = "|".join(waypoints)
        logger.debug(f"Using {len(waypoints)} waypoints for route")

    if avoid_highways:
        params["avoid"] = "highways"

    # Request alternative routes for variety
    params["alternatives"] = "true"

    try:
        logger.debug("Calling Google Maps Directions API")
        response = requests.get(url, params=params)
        data = response.json()

        duration_ms = int((time.time() - start_time) * 1000)

        if data['status'] == 'OK':
            # Get the best route (or first alternative)
            route = data['routes'][0]
            legs = route['legs']

            # Extract path coordinates
            path_coordinates = []
            for leg in legs:
                for step in leg['steps']:
                    path_coordinates.append((
                        step['start_location']['lat'],
                        step['start_location']['lng']
                    ))
            path_coordinates.append((
                legs[-1]['end_location']['lat'],
                legs[-1]['end_location']['lng']
            ))

            total_distance = sum(leg['distance']['value'] for leg in legs)
            total_distance_km = total_distance / 1000

            logger.info(
                "Running directions retrieved successfully",
                extra={
                    "agent_name": "route_builder",
                    "duration_ms": duration_ms,
                    "total_distance_km": round(total_distance_km, 2),
                    "num_routes": len(data['routes']),
                    "num_coordinates": len(path_coordinates)
                }
            )

            return {
                "status": "success",
                "total_distance": total_distance,
                "path_coordinates": path_coordinates,
                "summary": route.get('summary', 'Route found'),
                "total_duration": sum(leg['duration']['value'] for leg in legs),
                "num_alternatives": len(data['routes']),
                "legs": [
                    {
                        "start_address": leg['start_address'],
                        "end_address": leg['end_address'],
                        "distance": leg['distance']['text'],
                        "duration": leg['duration']['text']
                    }
                    for leg in legs
                ]
            }
        else:
            logger.warning(
                f"Directions API error: {data['status']}",
                extra={
                    "agent_name": "route_builder",
                    "duration_ms": duration_ms,
                    "api_status": data['status'],
                    "origin": origin,
                    "destination": destination
                }
            )
            return {
                "status": "error",
                "error_message": f"Directions API returned: {data['status']}"
            }

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            f"Error getting running directions: {str(e)}",
            exc_info=True,
            extra={
                "agent_name": "route_builder",
                "duration_ms": duration_ms,
                "error_type": type(e).__name__
            }
        )
        return {
            "status": "error",
            "error_message": str(e)
        }


def generate_google_maps_url(
    origin: str,
    destination: str,
    waypoints: List[str] = None,
    travel_mode: str = "walking"
) -> Dict:
    """
    Generate a Google Maps URL to view the route.

    Args:
        origin: Starting location
        destination: Ending location
        waypoints: Optional list of waypoints
        travel_mode: driving, walking, bicycling, or transit

    Returns:
        dict: Contains the Google Maps URL
    """
    logger.info(
        "Generating Google Maps URL",
        extra={
            "agent_name": "route_builder",
            "origin": origin,
            "destination": destination,
            "waypoint_count": len(waypoints) if waypoints else 0,
            "travel_mode": travel_mode
        }
    )

    try:
        base_url = "https://www.google.com/maps/dir/"

        # URL encode locations
        encoded_origin = quote(origin)
        encoded_destination = quote(destination)

        # Build URL with waypoints
        if waypoints:
            encoded_waypoints = "/".join([quote(wp) for wp in waypoints])
            url = f"{base_url}{encoded_origin}/{encoded_waypoints}/{encoded_destination}"
            logger.debug(f"Generated URL with {len(waypoints)} waypoints")
        else:
            url = f"{base_url}{encoded_origin}/{encoded_destination}"
            logger.debug("Generated direct route URL")

        # Add travel mode parameter
        url += f"/@?travelmode={travel_mode}"

        logger.info(
            "Google Maps URL generated successfully",
            extra={
                "agent_name": "route_builder",
                "url_length": len(url)
            }
        )

        return {
            "status": "success",
            "maps_url": url,
            "message": f"Click here to view route in Google Maps: {url}"
        }

    except Exception as e:
        logger.error(
            f"Error generating Google Maps URL: {str(e)}",
            exc_info=True,
            extra={
                "agent_name": "route_builder",
                "error_type": type(e).__name__
            }
        )
        return {
            "status": "error",
            "error_message": str(e)
        }