import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LinkedIn authentication
connections_file = 'connections.csv'
linkedin_username = os.getenv('LINKEDIN_USERNAME')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')

# If credentials are not set, warn the user
if not linkedin_username or not linkedin_password:
    print("WARNING: LinkedIn credentials not found in .env file")
    print("Please set LINKEDIN_USERNAME and LINKEDIN_PASSWORD in your .env file")

# Search parameters
search_keywords = 'DevOps,Linux,Python,AWS'
exclude_connections = ''
max_pages_to_search = 1

# Connection limits
max_connections_per_day = 20  # LinkedIn typically allows ~100 per week
max_connections_per_session = 10  # Stop after this many in a single run

# Gemini API configuration
gemini_api_key = os.getenv('GEMINI_API_KEY')  # Loaded from .env file
enable_gemini_analysis = True

# Rate limiting configuration
connection_delay_seconds = 5  # Time to wait between connection requests
