import requests
from typing import Dict, List, Optional
from config import settings

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
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "walking",  # Walking mode for runners
        "key": settings.google_maps_api_key
    }
    
    if waypoints:
        params["waypoints"] = "|".join(waypoints)
    
    if avoid_highways:
        params["avoid"] = "highways"
    
    # Request alternative routes for variety
    params["alternatives"] = "true"
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
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
            return {
                "status": "error",
                "error_message": f"Directions API returned: {data['status']}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }