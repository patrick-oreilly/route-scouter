import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext, AgentTool
from google.adk.planners import PlanReActPlanner
from typing import Dict, List, Optional
from google.adk.models.lite_llm import LiteLlm
from . import prompt
from . import tools
from ..google_search_agent import google_search_agent
import logging

AGENT_NAME="location_scout"
logger = logging.getLogger(__name__)


def scout_running_location(
    location_name: str,
    tool_context: ToolContext
) -> Dict:
    """
    Get detailed information about a running location.
    
    Args:
        location_name: Name of the location to scout
        
    Returns:
        dict: Location coordinates and details
    """
    
    logger.info("scout_running_location tool used")
    result = tools.geocode_location(location_name)
    
    if result['status'] == 'success' and tool_context:
        tool_context.state[f'location_{location_name}'] = {
            'lat': result['latitude'],
            'lng': result['longitude']
        }
    
    return result


def find_runner_amenities(
    latitude: float,
    longitude: float,
    amenity_type: str,
    radius: int = 2000,
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

    logger.info("find_runner_amenities tool used")
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
    
    result = tools.find_nearby_places(
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
) -> Dict:
    """
    Find good starting points for runs (parks, trails, waterfronts).
    
    Args:
        location: General area to search
        
    Returns:
        dict: Suggested starting points for runs
    """
    logger.info("find_running_start_points tool used")
    # First geocode the location
    geocode_result = tools.geocode_location(location)
    
    if geocode_result['status'] != 'success':
        return geocode_result
    
    lat = geocode_result['latitude']
    lng = geocode_result['longitude']
    
    # Find parks (great running spots)
    parks = tools.find_nearby_places(
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

location_scout = Agent(
    name=AGENT_NAME,
    model=LiteLlm(model=os.getenv("OPENAI_MODEL","GROK_MODEL")),
    description=(
        "Scouts locations and finds runner-friendly amenities"
        "like water fountains, restrooms, parks, and safe starting points for runs."
    ),
    planner=PlanReActPlanner(),
    instruction=prompt.LOCATION_SCOUT_PROMPT,
    output_key="location_scouting",
    tools=[scout_running_location, find_runner_amenities, find_running_start_points, AgentTool(agent=google_search_agent)]
)