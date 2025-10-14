from typing import List, Dict
from urllib.parse import quote

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
    base_url = "https://www.google.com/maps/dir/"
    
    # URL encode locations
    encoded_origin = quote(origin)
    encoded_destination = quote(destination)
    
    # Build URL with waypoints
    if waypoints:
        encoded_waypoints = "/".join([quote(wp) for wp in waypoints])
        url = f"{base_url}{encoded_origin}/{encoded_waypoints}/{encoded_destination}"
    else:
        url = f"{base_url}{encoded_origin}/{encoded_destination}"
    
    # Add travel mode parameter
    url += f"/@?travelmode={travel_mode}"
    
    return {
        "status": "success",
        "maps_url": url,
        "message": f"Click here to view route in Google Maps: {url}"
    }


def generate_maps_url_from_coordinates(
    coordinates: List[tuple],
    travel_mode: str = "walking"
) -> Dict:
    """
    Generate Google Maps URL from a list of coordinates.
    
    Args:
        coordinates: List of (lat, lng) tuples
        travel_mode: walking, driving, bicycling, or transit
        
    Returns:
        dict: Contains the Google Maps URL
    """
    if len(coordinates) < 2:
        return {
            "status": "error",
            "error_message": "Need at least 2 coordinates for a route"
        }
    
    base_url = "https://www.google.com/maps/dir/"
    
    # Format coordinates as lat,lng
    coord_strings = [f"{lat},{lng}" for lat, lng in coordinates]
    
    # Join with slashes
    url = base_url + "/".join(coord_strings)
    url += f"/@?travelmode={travel_mode}"
    
    return {
        "status": "success",
        "maps_url": url,
        "message": f"View route in Google Maps: {url}"
    }


def generate_place_marker_url(
    latitude: float,
    longitude: float,
    label: str = None
) -> Dict:
    """
    Generate a Google Maps URL with a marker at a specific location.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        label: Optional label for the marker
        
    Returns:
        dict: Contains the Google Maps URL with marker
    """
    # Format: https://www.google.com/maps/search/?api=1&query=lat,lng
    base_url = "https://www.google.com/maps/search/"
    url = f"{base_url}?api=1&query={latitude},{longitude}"
    
    if label:
        url += f"&query_place_id={quote(label)}"
    
    return {
        "status": "success",
        "maps_url": url,
        "message": f"View location in Google Maps: {url}"
    }