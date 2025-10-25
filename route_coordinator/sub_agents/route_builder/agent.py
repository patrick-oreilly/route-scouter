import os
import math
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, List, Optional
from google.adk.models.lite_llm import LiteLlm

from . import prompt
from . import tools
from ..location_scout.tools import geocode_location
import logging

AGENT_NAME="route_builder"
logger = logging.getLogger(__name__)


def _generate_loop_waypoints(lat: float, lng: float, distance_km: float, num_points: int = 4) -> List[str]:
    """
    Generate waypoints to create a loop route.

    Creates waypoints in a circular pattern around the start point.
    The actual route distance will follow streets and may vary from the target.

    Args:
        lat: Starting latitude
        lng: Starting longitude
        distance_km: Target total loop distance
        num_points: Number of waypoints (default 4)

    Returns:
        List of waypoint strings in "lat,lng" format
    """
    logger.info("_generate_loop_waypoints tool used")
    # For a loop with N waypoints, estimate the radius needed
    # Assume the route follows streets (Manhattan distance factor ~1.3)
    # Perimeter = distance_km, so radius ≈ distance_km / (2 * π * 1.3)
    manhattan_factor = 1.3
    radius_km = distance_km / (2 * math.pi * manhattan_factor)

    # Convert km to degrees (approximate)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_offset = radius_km / 111
    lng_offset = radius_km / (111 * math.cos(math.radians(lat)))

    waypoints = []

    # Generate waypoints evenly distributed around a circle
    # Start at 45° to create a more natural route pattern
    angle_step = 360 / num_points
    start_angle = 45

    for i in range(num_points):
        angle = start_angle + (i * angle_step)
        angle_rad = math.radians(angle)
        wp_lat = lat + (lat_offset * math.sin(angle_rad))
        wp_lng = lng + (lng_offset * math.cos(angle_rad))
        waypoints.append(f"{wp_lat},{wp_lng}")

    return waypoints


def _generate_out_and_back_waypoint(lat: float, lng: float, distance_km: float, direction: float) -> List[str]:
    """
    Generate a single waypoint for an out-and-back route.

    Creates one waypoint in the specified direction from the start point.
    The route will go from start -> waypoint -> back to start.
    Total distance should be approximately the target distance.

    Args:
        lat: Starting latitude
        lng: Starting longitude
        distance_km: Target total distance (round-trip)
        direction: Direction in degrees (0=North, 90=East, 180=South, 270=West)

    Returns:
        List with a single waypoint string in "lat,lng" format
    """
    logger.info("_generate_out_and_back_waypoint tool used")

    # For out-and-back, the waypoint should be at half the target distance
    # Account for street following (Manhattan distance factor ~1.3)
    manhattan_factor = 1.3
    one_way_distance_km = (distance_km / 2) / manhattan_factor

    # Convert km to degrees (approximate)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)
    lat_offset_per_km = 1 / 111
    lng_offset_per_km = 1 / (111 * math.cos(math.radians(lat)))

    # Calculate waypoint position based on direction
    direction_rad = math.radians(direction)
    wp_lat = lat + (one_way_distance_km * lat_offset_per_km * math.cos(direction_rad))
    wp_lng = lng + (one_way_distance_km * lng_offset_per_km * math.sin(direction_rad))

    return [f"{wp_lat},{wp_lng}"]


def find_running_route(
    start_location: str,
    end_location: Optional[str] = None,
    distance_target_km: Optional[float] = None,
    is_loop: bool = False,
    tool_context: ToolContext = None
) -> Dict:
    """
    Find the best running route.

    Args:
        start_location: Starting point (name or coordinates)
        end_location: Destination (if point-to-point), None for out-and-back
        distance_target_km: Target distance in kilometers (required for loops and out-and-backs)
        is_loop: True if creating a loop route

    Returns:
        dict: Route details including path, distance, pace estimates, and Google Maps URL
    """
    logger.info("find_running_route tool used")

    waypoints = None

    # Generate loop with waypoints if requested
    if is_loop:
        if not distance_target_km:
            return {
                "status": "error",
                "error_message": "distance_target_km is required when is_loop=True"
            }

        # Geocode the start location to get coordinates
        coords = geocode_location(start_location)
        if coords['status'] != 'success':
            return coords

        # Generate waypoints for the loop
        waypoints = _generate_loop_waypoints(
            coords['latitude'],
            coords['longitude'],
            distance_target_km
        )

        # For a loop, end where we start
        end_location = start_location

    # If no end location and not a loop, make it out-and-back with a waypoint
    elif not end_location:
        if not distance_target_km:
            return {
                "status": "error",
                "error_message": "distance_target_km is required for out-and-back routes"
            }

        # Geocode the start location to get coordinates
        coords = geocode_location(start_location)
        if coords['status'] != 'success':
            return coords

        # Generate a single waypoint for out-and-back
        # Use direction=0 (North) by default, could be randomized or user-specified
        waypoints = _generate_out_and_back_waypoint(
            coords['latitude'],
            coords['longitude'],
            distance_target_km,
            direction=0
        )

        # For out-and-back, end where we start
        end_location = start_location

    result = tools.get_running_directions(
        origin=start_location,
        destination=end_location,
        waypoints=waypoints
    )
    
    if result['status'] == 'success':
        # Convert distance to km
        distance_km = result['total_distance'] / 1000
        
        # Calculate pace estimates for different runner levels
        # Base walking time from API, convert to running estimates
        base_minutes = result['total_duration'] / 60
        
        # Typical running paces (min/km)
        easy_pace = 6.5  # 6:30/km
        moderate_pace = 5.5  # 5:30/km
        fast_pace = 4.5  # 4:30/km
        
        result['distance_km'] = round(distance_km, 2)
        result['estimated_times'] = {
            'easy_pace': f"{distance_km * easy_pace:.0f} min ({easy_pace:.1f} min/km)",
            'moderate_pace': f"{distance_km * moderate_pace:.0f} min ({moderate_pace:.1f} min/km)",
            'fast_pace': f"{distance_km * fast_pace:.0f} min ({fast_pace:.1f} min/km)"
        }
        
        # Generate Google Maps URL (include waypoints if they exist)
        maps_url = tools.generate_google_maps_url(
            origin=start_location,
            destination=end_location,
            waypoints=waypoints,
            travel_mode="walking"  # Use walking for running routes
        )
        result['google_maps_url'] = maps_url['maps_url']
        
        # Store coordinates for elevation agent
        if tool_context:
            tool_context.state['route_coordinates'] = result['path_coordinates']
            tool_context.state['route_distance_km'] = distance_km
    
    return result


def suggest_loop_routes(
    location: str,
    distance_km: float ,
    tool_context: ToolContext
) -> Dict:
    """
    Suggest and generate loop routes from a starting location.

    This function now generates an actual loop route using waypoints.

    Args:
        location: Starting location
        distance_km: Desired loop distance in km

    Returns:
        dict: Generated loop route with details
    """
    logger.info("suggest_loop_routes tool used")
    # Use find_running_route with is_loop=True to generate an actual loop
    return find_running_route(
        start_location=location,
        distance_target_km=distance_km,
        is_loop=True,
        tool_context=tool_context
    )


route_builder = Agent(
    name=AGENT_NAME,
    model=LiteLlm(model=os.getenv("OPENAI_MODEL","GROK_MODEL")),
    description=(
        "Finds optimal running routes including loops, out-and-backs,"
        "and point-to-point courses. Calculates distances and provides pace estimates."
    ),
    instruction=prompt.ROUTE_BUILDER_PROMPT,
    output_key="route_builder_response",
    tools=[find_running_route, suggest_loop_routes]
)