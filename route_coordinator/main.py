"""Main entry point for the Route Scout Agent."""

from google.adk.sessions import Session
from .agent import root_agent


def main():
    """Run the route scout agent interactively."""
    print("🏃 Route Scout Agent")
    print("=" * 50)
    print("Find running routes with distance, elevation, and amenities")
    print("Example: 'Find me a scenic 5k in Galway City'")
    print("=" * 50)
    print()

    session = Session(agent=root_agent)
    session.run()


if __name__ == "__main__":
    main()
