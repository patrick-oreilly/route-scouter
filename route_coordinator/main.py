"""Main entry point for the Route Scout Agent."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.sessions import Session
from .agent import root_agent
from logging_config import setup_logging, get_logger

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_format=os.getenv("LOG_FORMAT", "console"),
    enable_file_logging=os.getenv("ENABLE_FILE_LOGGING", "true").lower() in ("true", "1", "yes")
)

logger = get_logger(__name__)


def main():
    """Run the route scout agent interactively."""
    logger.info("=" * 60)
    logger.info("Starting Route Scout Agent (Interactive Mode)")
    logger.info("=" * 60)

    print("🏃 Route Scout Agent")
    print("=" * 50)
    print("Find running routes with distance, elevation, and amenities")
    print("Example: 'Find me a scenic 5k in Galway City'")
    print("=" * 50)
    print()

    try:
        logger.info("Creating agent session")
        session = Session(agent=root_agent)

        logger.info("Starting interactive session")
        session.run()

        logger.info("Session ended")

    except KeyboardInterrupt:
        logger.info("Session interrupted by user")
        print("\nGoodbye!")
    except Exception as e:
        logger.error(f"Error running agent session: {str(e)}", exc_info=True)
        print(f"\nError: {str(e)}")
        raise


if __name__ == "__main__":
    main()
