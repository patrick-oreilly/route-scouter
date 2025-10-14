import os
import math
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, List, Optional
from tools.directions_tools import get_running_directions
from tools.maps_url_tools import generate_google_maps_url

def _geocode_location(location: str) -> Optional[Dict]:
    """Helper to convert location string to lat/lng coordinates."""
    import requests
    from config import settings

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location,
        "key": settings.google_maps_api_key
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {'lat': loc['lat'], 'lng': loc['lng']}
        return None
    except:
        return None


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
        distance_target_km: Target distance in kilometers (required for loops)
        is_loop: True if creating a loop route

    Returns:
        dict: Route details including path, distance, pace estimates, and Google Maps URL
    """
    waypoints = None

    # Generate loop with waypoints if requested
    if is_loop:
        if not distance_target_km:
            return {
                "status": "error",
                "error_message": "distance_target_km is required when is_loop=True"
            }

        # Geocode the start location to get coordinates
        coords = _geocode_location(start_location)
        if not coords:
            return {
                "status": "error",
                "error_message": f"Could not geocode location: {start_location}"
            }

        # Generate waypoints for the loop
        waypoints = _generate_loop_waypoints(
            coords['lat'],
            coords['lng'],
            distance_target_km
        )

        # For a loop, end where we start
        end_location = start_location

    # If no end location and not a loop, make it out-and-back (same as start)
    if not end_location:
        end_location = start_location

    result = get_running_directions(
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
        maps_url = generate_google_maps_url(
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
    distance_km: float = 5.0,
    tool_context: ToolContext = None
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
    # Use find_running_route with is_loop=True to generate an actual loop
    return find_running_route(
        start_location=location,
        distance_target_km=distance_km,
        is_loop=True,
        tool_context=tool_context
    )


route_finding_agent = Agent(
    name="RouteFindingAgent",
    model="gemini-2.0-flash",
    description="Finds optimal running routes including loops, out-and-backs, and point-to-point courses. Calculates distances and provides pace estimates.",
    instruction="""You are a route planning specialist for runners.

    **MANDATORY PROCESS - ALWAYS use tools, never estimate:**

    1. **Identify route type from the request:**
       - Loop route (starts and ends at same place, with waypoints)
       - Point-to-point (different start and end)
       - Out-and-back (returns to start, no waypoints)

    2. **Call the appropriate tool:**
       - For loop routes: Call suggest_loop_routes with exact distance_km requested
       - For point-to-point: Call find_running_route with start_location and end_location
       - For out-and-back: Call find_running_route with start_location only
       - NEVER skip tool calling or provide estimates

    3. **Wait for tool results and verify you have:**
       - total_distance or distance_km
       - estimated_times (easy, moderate, fast paces)
       - google_maps_url
       - path_coordinates (critical for elevation agent)

    4. **Verify tool_context storage:**
       - Confirm route_coordinates are stored in tool_context
       - Confirm route_distance_km is stored in tool_context
       - This data is required for the elevation_analysis_agent

    **CRITICAL RULES:**

    - NEVER respond without calling a tool first
    - Use the EXACT distance the user requests (don't suggest alternatives)
    - ALWAYS wait for tool results before responding
    - Do NOT discuss what you can or cannot do - just call tools
    - Do NOT mention elevation, hilliness, or other agents
    - Present ONLY factual data from tool results

    **Response Format (only after tool completes):**

    🏃 Generated [X]km [loop/point-to-point/out-and-back] route:

    📍 Distance: [X.X] km (from tool result)
    🗺️ Route: [Start] → [waypoints if loop] → [End]

    ⏱️ Estimated Times:
       • Easy pace (6:30/km): [XX] min
       • Moderate pace (5:30/km): [XX] min
       • Fast pace (4:30/km): [XX] min

    🗺️ View Route: [Google Maps URL from tool]

    ✓ Route coordinates stored for elevation analysis

    ALWAYS include the Google Maps URL. Never estimate - only use tool data.""",
    tools=[find_running_route, suggest_loop_routes]
)