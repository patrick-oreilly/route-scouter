import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, List
from tools.elevation_tools import get_elevation_along_path

def analyze_elevation_for_runners(
    path_coordinates: List[List[float]],
    samples: int = 100,
    tool_context: ToolContext = None
) -> Dict:
    """
    Analyze elevation profile for running routes.
    
    Args:
        path_coordinates: List of [lat, lng] coordinate pairs
        samples: Number of elevation samples (default 100 for detailed profile)
        
    Returns:
        dict: Elevation analysis with training insights for runners
    """
    # Convert to tuples for the API
    path_tuples = [(coord[0], coord[1]) for coord in path_coordinates]
    
    result = get_elevation_along_path(path_tuples, samples)
    
    if result['status'] == 'success':
        gain = result['total_elevation_gain']
        loss = result['total_elevation_loss']
        
        # Runner-specific difficulty assessment
        if gain < 50:
            difficulty = "Flat - Great for speed work"
            training_benefit = "Perfect for tempo runs and interval training"
        elif gain < 150:
            difficulty = "Rolling - Moderate hills"
            training_benefit = "Good for building leg strength and endurance"
        elif gain < 300:
            difficulty = "Hilly - Challenging"
            training_benefit = "Excellent hill training, builds power and stamina"
        else:
            difficulty = "Very Hilly - Advanced"
            training_benefit = "Serious hill work, great for race prep and strength"
        
        # Calculate average grade
        total_distance_m = sum([
            ((result['elevation_profile'][i]['lat'] - result['elevation_profile'][i-1]['lat'])**2 +
             (result['elevation_profile'][i]['lng'] - result['elevation_profile'][i-1]['lng'])**2)**0.5 * 111000
            for i in range(1, len(result['elevation_profile']))
        ])
        avg_grade = (gain / total_distance_m * 100) if total_distance_m > 0 else 0
        
        result['difficulty_rating'] = difficulty
        result['training_benefit'] = training_benefit
        result['average_grade'] = round(avg_grade, 2)
        result['runner_recommendation'] = (
            f"This route has {gain:.0f}m elevation gain over approximately "
            f"{total_distance_m/1000:.1f}km. {difficulty}. {training_benefit}."
        )
    
    return result


elevation_analysis_agent = Agent(
    name="ElevationAnalysisAgent",
    model="gemini-2.0-flash",
    description="Analyzes elevation profiles and terrain for running routes. Specializes in identifying flat routes, hills, and elevation changes relevant to runners.",
    instruction="""You are an elevation analysis specialist for running routes.

    **MANDATORY PROCESS - ALWAYS analyze, never estimate:**

    1. **First, retrieve route data from tool_context:**
       - Look for 'route_coordinates' (list of lat/lng pairs from route_finding_agent)
       - Look for 'route_distance_km' (total distance)
       - If missing, report error and request coordinator to run route_finding_agent first

    2. **Then call analyze_elevation_for_runners:**
       - Use path_coordinates from tool_context
       - Use samples=100 for detailed elevation profile
       - NEVER skip this tool call or provide estimates
       - Wait for complete results before responding

    3. **Extract ALL metrics from tool results:**
       - total_elevation_gain (meters)
       - total_elevation_loss (meters)
       - difficulty_rating (Flat/Rolling/Hilly/Very Hilly)
       - training_benefit (speed work, hill training, etc.)
       - average_grade (percentage)
       - elevation_profile (detailed points)

    **CRITICAL RULES:**

    - NEVER respond without calling analyze_elevation_for_runners first
    - NEVER estimate or guess elevation data
    - ALWAYS use at least 100 samples for accuracy
    - Present ONLY factual data from tool results
    - Do NOT mention other agents or capabilities

    **Response Format (only after tool completes):**

    ⛰️ Elevation Analysis Complete:

    📊 Terrain Profile:
       • Elevation Gain: [X]m
       • Elevation Loss: [X]m
       • Average Grade: [X.X]%
       • Difficulty: [Flat/Rolling/Hilly/Very Hilly]

    💪 Training Benefits:
       • [Specific training benefit from tool]
       • [Additional insights about hills/climbs]

    🏃 Recommended For:
       • [Type of workout this terrain suits]
       • [Specific training advice]

    📈 Notable Features:
       • [Any significant climbs or descents]
       • [Terrain characteristics]

    Present detailed, specific analysis from actual elevation data only.""",
    tools=[analyze_elevation_for_runners]
)