from google.adk.agents import Agent
from google.adk.tools import ToolContext
from typing import Dict, List
from . import prompt
from . import tools

AGENT_NAME="elevation_analyst"
MODEL = "gemini-2.0-flash"

def analyze_elevation_for_runners(
    path_coordinates: List[List[float]],
    samples: int,
    tool_context: ToolContext
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
    
    result = tools.get_elevation_along_path(path_tuples, samples)
    
    if result['status'] == 'success':
        gain = result['total_elevation_gain']

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


elevation_analyst = Agent(
    name=AGENT_NAME,
    model=MODEL,
    description=(
        "Analyzes elevation profiles and terrain for running routes." 
        "Specializes in identifying flat routes, hills, and elevation"
        "changes relevant to runners."
    ),
    instruction=prompt.ELEVATION_ANALYST_PROMPT,
    output_key="elevation_analysis_response",
    tools=[analyze_elevation_for_runners]
)