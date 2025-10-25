import os
import requests
from typing import Dict, List, Tuple
import math

STRAVA_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
HIKING_PROJECT_KEY = os.getenv("HIKING_PROJECT_API_KEY")
MAPBOX_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

def get_popular_running_routes_strava(
    lat: float,
    lng: float,
    radius_km: float = 5
) -> Dict:
    """
    Get popular running routes from Strava in an area.
    
    Returns actual routes that real runners use!
    """
    # Create bounding box
    lat_offset = radius_km / 111  # Rough conversion
    lng_offset = radius_km / (111 * abs(math.cos(math.radians(lat))))
    
    bounds = (
        lat - lat_offset,  # SW lat
        lng - lng_offset,  # SW lng
        lat + lat_offset,  # NE lat
        lng + lng_offset   # NE lng
    )
    
    url = "https://www.strava.com/api/v3/segments/explore"
    
    headers = {"Authorization": f"Bearer {STRAVA_TOKEN}"}
    params = {
        "bounds": f"{bounds[0]},{bounds[1]},{bounds[2]},{bounds[3]}",
        "activity_type": "running"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if 'segments' in data:
            routes = []
            for segment in data['segments'][:10]:  # Top 10
                routes.append({
                    "name": segment['name'],
                    "distance": segment['distance'],  # meters
                    "avg_grade": segment['avg_grade'],
                    "elevation_difference": segment['elev_difference'],
                    "climb_category": segment['climb_category'],
                    "athlete_count": segment['athlete_count'],
                    "effort_count": segment['effort_count'],
                    "polyline": segment['points'],  # Encoded polyline
                    "start_latlng": segment['start_latlng'],
                    "end_latlng": segment['end_latlng']
                })
            
            return {
                "status": "success",
                "source": "strava",
                "routes": routes,
                "count": len(routes)
            }
        else:
            return {
                "status": "error",
                "error_message": "No segments found"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


def get_trail_running_routes(
    lat: float,
    lng: float,
    max_distance: int = 10
) -> Dict:
    """
    Get trail running routes from Hiking Project API.
    """
    url = "https://www.hikingproject.com/data/get-trails"
    params = {
        "lat": lat,
        "lon": lng,
        "maxDistance": max_distance,
        "maxResults": 10,
        "key": HIKING_PROJECT_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'trails' in data:
            routes = []
            for trail in data['trails']:
                routes.append({
                    "name": trail['name'],
                    "distance_miles": trail['length'],
                    "distance_km": trail['length'] * 1.609,
                    "elevation_gain": trail['ascent'],
                    "difficulty": trail['difficulty'],
                    "stars": trail['stars'],
                    "location": trail['location'],
                    "summary": trail['summary'],
                    "lat": trail['latitude'],
                    "lng": trail['longitude'],
                    "condition": trail.get('conditionStatus', 'Unknown')
                })
            
            return {
                "status": "success",
                "source": "hiking_project",
                "routes": routes,
                "count": len(routes)
            }
        else:
            return {
                "status": "error",
                "error_message": "No trails found"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


def get_best_running_route(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float
) -> Dict:
    """
    Get optimized running route using Mapbox (better than Google for pedestrian paths).
    """
    url = f"https://api.mapbox.com/directions/v5/mapbox/walking/{start_lng},{start_lat};{end_lng},{end_lat}"
    
    params = {
        "alternatives": "true",
        "geometries": "geojson",
        "steps": "true",
        "banner_instructions": "true",
        "access_token": MAPBOX_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'routes' in data and len(data['routes']) > 0:
            route = data['routes'][0]
            
            return {
                "status": "success",
                "source": "mapbox",
                "distance": route['distance'],  # meters
                "duration": route['duration'],  # seconds
                "geometry": route['geometry'],  # GeoJSON
                "legs": route['legs'],
                "alternatives": len(data['routes'])
            }
        else:
            return {
                "status": "error",
                "error_message": "No route found"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }