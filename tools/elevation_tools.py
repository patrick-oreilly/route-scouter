import requests
from typing import Dict, List, Tuple
from config import settings

def get_elevation_data(lat: float, lng: float) -> Dict:
    """
    Get elevation for a single location.
    
    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        
    Returns:
        dict: Contains 'status', 'elevation' (in meters), and 'resolution'
    """
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        "locations": f"{lat},{lng}",
        "key": settings.google_maps_api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            result = data['results'][0]
            return {
                "status": "success",
                "elevation": result['elevation'],
                "resolution": result['resolution'],
                "location": result['location']
            }
        else:
            return {
                "status": "error",
                "error_message": f"API returned status: {data['status']}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


def get_elevation_along_path(
    path_points: List[Tuple[float, float]], 
    samples: int,
) -> Dict:
    """
    Get elevation profile along a hiking path.
    
    Args:
        path_points: List of (lat, lng) tuples defining the path
        samples: Number of elevation samples along the path
        
    Returns:
        dict: Contains 'status' and elevation profile data
    """
    url = "https://maps.googleapis.com/maps/api/elevation/json"
    
    # Format path as pipe-separated coordinates
    path_str = "|".join([f"{lat},{lng}" for lat, lng in path_points])
    
    params = {
        "path": path_str,
        "samples": samples,
        "key": settings.google_maps_api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            elevations = [
                {
                    "lat": r['location']['lat'],
                    "lng": r['location']['lng'],
                    "elevation": r['elevation']
                }
                for r in data['results']
            ]
            
            # Calculate elevation gain/loss
            total_gain = sum(
                max(0, elevations[i]['elevation'] - elevations[i-1]['elevation'])
                for i in range(1, len(elevations))
            )
            total_loss = sum(
                max(0, elevations[i-1]['elevation'] - elevations[i]['elevation'])
                for i in range(1, len(elevations))
            )
            
            return {
                "status": "success",
                "elevation_profile": elevations,
                "total_elevation_gain": round(total_gain, 2),
                "total_elevation_loss": round(total_loss, 2),
                "max_elevation": max(e['elevation'] for e in elevations),
                "min_elevation": min(e['elevation'] for e in elevations)
            }
        else:
            return {
                "status": "error",
                "error_message": f"API returned status: {data['status']}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }