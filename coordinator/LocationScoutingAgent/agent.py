import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict
from tools.places_tools import geocode_location, find_nearby_places


def scout_running_location(
    location_name: str,
    tool_context: ToolContext = None
) -> Dict:
    """
    Get detailed information about a running location.
    
    Args:
        location_name: Name of the location to scout
        
    Returns:
        dict: Location coordinates and details
    """
    result = geocode_location(location_name)
    
    if result['status'] == 'success' and tool_context:
        tool_context.state[f'location_{location_name}'] = {
            'lat': result['latitude'],
            'lng': result['longitude']
        }
    
    return result


def find_runner_amenities(
    latitude: float,
    longitude: float,
    amenity_type: str = "restroom",
    radius: int = 2000,
    tool_context: ToolContext = None
) -> Dict:
    """
    Find runner-friendly amenities along routes.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        amenity_type: Type of amenity (restroom, park, water_fountain, cafe, etc.)
        radius: Search radius in meters (default 2km)
        
    Returns:
        dict: Nearby runner amenities
    """
    # Map runner-friendly amenity types to Google Places API types
    amenity_mapping = {
        "restroom": "toilet",
        "water": "park",  # Parks often have water fountains
        "cafe": "cafe",
        "park": "park",
        "gym": "gym",
        "store": "convenience_store"
    }
    
    places_type = amenity_mapping.get(amenity_type.lower(), amenity_type)
    
    result = find_nearby_places(
        lat=latitude,
        lng=longitude,
        place_type=places_type,
        radius=radius,
    )
    
    if result['status'] == 'success':
        result['amenity_type'] = amenity_type
        result['message'] = f"Found {result['count']} {amenity_type} locations within {radius}m"
    
    return result


def find_running_start_points(
    location: str,
    tool_context: ToolContext = None
) -> Dict:
    """
    Find good starting points for runs (parks, trails, waterfronts).
    
    Args:
        location: General area to search
        
    Returns:
        dict: Suggested starting points for runs
    """
    # First geocode the location
    geocode_result = geocode_location(location)
    
    if geocode_result['status'] != 'success':
        return geocode_result
    
    lat = geocode_result['latitude']
    lng = geocode_result['longitude']
    
    # Find parks (great running spots)
    parks = find_nearby_places(
        lat=lat,
        lng=lng,
        place_type="park",
        radius=5000,
    )
    
    return {
        "status": "success",
        "location": location,
        "coordinates": {"lat": lat, "lng": lng},
        "nearby_parks": parks.get('places', []) if parks['status'] == 'success' else [],
        "recommendation": "Parks are excellent starting points with paths, water, and restrooms"
    }

location_scouting_agent = Agent(
    name="LocationScoutingAgent",
    model="gemini-2.0-flash",
    description="Scouts locations and finds runner-friendly amenities like water fountains, restrooms, parks, and safe starting points for runs.",
    instruction="""You are a location scouting specialist for runners.

    **MANDATORY PROCESS - Use multiple tools for thorough research:**

    1. **ALWAYS start with scout_running_location**:
       - Convert the location name to precise coordinates
       - Store coordinates in tool_context for other agents to use
       - Wait for results before proceeding

    2. **Then call find_running_start_points**:
       - Identify nearby parks and good starting areas
       - Even if user specified exact location, suggest alternatives
       - Find at least 2-3 potential starting points
       - Wait for results before proceeding

    3. **Then call find_runner_amenities multiple times** for different amenity types:
       - Call with amenity_type="restroom" (critical for long runs)
       - Call with amenity_type="cafe" (hydration and bathrooms)
       - Call with amenity_type="park" (safe, scenic areas)
       - You MUST make at least 3 separate calls to this tool
       - Use appropriate radius (2000m for restrooms/cafes, 5000m for parks)

    **CRITICAL RULES:**

    - NEVER respond without calling ALL tools first
    - You MUST call at least 4 tools total (1 scout + 1 start points + 2+ amenities)
    - Wait for each tool to return results before calling the next
    - Do NOT skip tools or provide estimates
    - Store all coordinates in tool_context for downstream agents

    **Response Format (only after all tool calls complete):**

    📍 Location Scouted: [Location Name]
       • Coordinates: [lat], [lng]
       • Area: [City/Region from geocoding]

    🏃 Recommended Starting Points:
       • [Park/Location 1] - [why it's good]
       • [Park/Location 2] - [why it's good]
       • [Park/Location 3] - [why it's good]

    🚻 Runner Amenities Found:
       • Restrooms: [X] within 2km
       • Cafes/Water: [X] within 2km
       • Parks: [X] within 5km

    💡 Safety Note: [Brief note about the area for running]

    Present ONLY factual data from your tool calls. Never skip research.""",
    tools=[scout_running_location, find_runner_amenities, find_running_start_points]
)