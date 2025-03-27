![](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Logo.svg.original.svg)
# LinkedIn Networking

Python code to automatically expand your LinkedIn network based on your interests with personalized messages using AI (Gemini or GPT-4o).

## Features

- Search LinkedIn for people based on keywords and location
- Filter connections by country
- Send personalized connection requests
- Generate AI-powered connection messages using either Google's Gemini AI or GPT-4o
- Log successful connections
- Exclude specific profiles
- Rate limiting and connection limits for account safety
- Automated browser interaction with anti-detection measures

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Either a Google Gemini API key or GPT-4o API key
- LinkedIn account

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/LinkedIn_networking.git
   cd LinkedIn_networking
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. Create a `.env` file in the root directory with the following variables:
   ```
   LINKEDIN_USERNAME=your_email@example.com
   LINKEDIN_PASSWORD=your_password_here
   GEMINI_API_KEY=your_gemini_api_key_here  # Optional if using GPT-4o
   gpt_4o=your_gpt4o_api_key_here  # Optional if using Gemini
   ```

2. Get your preferred AI API key:
   - For Gemini: Visit https://makersuite.google.com/app/apikey
   - For GPT-4o: Use your existing GPT-4o API key

3. Configure settings in `config/parameters.py`:
   ```python
   # Search parameters
   search_keywords = 'Your, Keywords, Here'  # Comma-separated
   search_country = 'Your Country Here'  # For reference only
   search_geo_urn = '103644278'  # LinkedIn's geoUrn ID for location filtering
   exclude_connections = ''  # Comma-separated list of names to skip
   max_pages_to_search = 1  # Number of search pages to process

   # Connection limits
   max_connections_per_day = 20  # LinkedIn typically allows ~100 per week
   max_connections_per_session = 10  # Stop after this many in a single run
   connection_delay_seconds = 5  # Time between requests

   # AI Configuration
   ai_provider = "gemini"  # Options: "gemini" or "gpt4o"
   enable_ai_analysis = True  # Toggle AI message generation
   gpt4o_endpoint = "https://models.inference.ai.azure.com"  # If using GPT-4o
   gpt4o_model = "gpt-4o"  # Model name for GPT-4o
   ```

## Usage

1. Test the AI integration (recommended before first use):
   ```bash
   python tests/test_gemini.py
   ```
   This will test both AI providers if you have configured them, validating:
   - API key configuration
   - Direct API connections
   - Message generation
   - Message processing and formatting

2. Run the main script:
   ```bash
   python src/linkedin/linkedIn.py
   ```

The script will:
- Log in to your LinkedIn account
- Search for profiles matching your keywords
- Generate personalized connection messages using your chosen AI provider
- Send connection requests while respecting rate limits
- Log successful connections in CSV format

## Command-Line Arguments

The script supports the following command-line arguments when running directly from the connector:

```bash
python src/linkedin/linkedin_connector.py --max-connections 15 --test-mode
```

Available arguments:
- `--max-connections` - Set the maximum number of connection requests to send in this session (overrides the default in parameters.py)
- `--test-mode` - Run in test mode with additional logging output

When running the main script (`linkedIn.py`), these arguments are passed through configuration in `parameters.py` rather than command-line arguments.

## Configuration Options

In `config/parameters.py`, you can customize:
- `search_keywords`: Comma-separated keywords for finding connections
- `search_country`: Country name (for reference only)
- `search_geo_urn`: LinkedIn's geoUrn ID for location filtering (e.g., "103644278" for United States)
- `exclude_connections`: Comma-separated list of profile names to skip
- `max_pages_to_search`: Number of search result pages to process
- `max_connections_per_day`: Daily connection request limit (default: 20)
- `max_connections_per_session`: Connection limit per script run (default: 10)
- `connection_delay_seconds`: Delay between requests (default: 5)
- `ai_provider`: Choose between "gemini" or "gpt4o"
- `enable_ai_analysis`: Toggle AI message generation (default: True)
- `gpt4o_endpoint`: API endpoint for GPT-4o (if using)
- `gpt4o_model`: Model name for GPT-4o requests
- `connections_file`: CSV file to log successful connections (default: 'connections.csv')

## Supported Countries

The script includes built-in geoUrn IDs for the following countries:
- United States (103644278)
- United Kingdom (101165590)
- Canada (101174742)
- Australia (101452733)
- India (102713980)
- Germany (101282230)
- France (105015875)
- Italy (103350119)
- Spain (105646813)
- Netherlands (102890719)

## Safety Features

- **Connection Limits**: Built-in daily and per-session limits
- **Rate Limiting**: Configurable delays between requests
- **Anti-Detection**: Browser automation masking
- **Safe Fallbacks**: Default messages if AI generation fails
- **Error Recovery**: Handles connection failures gracefully

## Important Notes

- **LinkedIn Limits**: LinkedIn restricts connection requests (~100/week)
- **CAPTCHA Handling**: Manual intervention needed if CAPTCHA appears
- **Account Safety**: Start with conservative limits and adjust based on your account age
- **API Usage**: Monitor your Gemini API quota usage
- **Terms of Service**: Use responsibly and in compliance with LinkedIn's terms

## Troubleshooting

1. If AI messages fail:
   - Verify your API key in `.env`
   - Run `tests/test_gemini.py` to diagnose issues
   - Check API quota and billing status
   - Verify the GPT-4o endpoint URL if using GPT-4o

2. If LinkedIn automation fails:
   - Check your credentials in `.env`
   - Verify internet connection
   - Ensure Chrome browser is installed
   - Try reducing connection frequency
   - Check if LinkedIn has updated their HTML structure
   - Clear browser cookies/cache if login issues persist

## Contributing

Pull requests are welcome. For major changes:
1. Open an issue first to discuss proposed changes
2. Update tests as needed
3. Follow the existing code style
4. Add comments for complex logic

## License

[GNU General Public License v3.0](LICENSE)

## Find me
[![](https://img.shields.io/badge/Find%20Me-LinkedIn-blue?style=flat-square)](https://www.linkedin.com/in/sreekar2858)
