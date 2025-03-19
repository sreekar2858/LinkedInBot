import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LinkedIn authentication
connections_file = 'connections.csv'
linkedin_username = os.getenv('LINKEDIN_USERNAME')
linkedin_password = os.getenv('LINKEDIN_PASSWORD')

# Search parameters
search_keywords = 'DevOps,Linux,Python,AWS'
exclude_connections = ''
max_pages_to_search = 1

# Gemini API configuration
gemini_api_key = os.getenv('GEMINI_API_KEY')  # Loaded from .env file
enable_gemini_analysis = True
