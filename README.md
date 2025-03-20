![](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Logo.svg.original.svg)
# LinkedIn Networking

Python code to automatically expand your LinkedIn network based on your interests with personalized messages using AI (Gemini or GPT-4o).

## Features

- Search LinkedIn for people based on keywords
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

3. Configure settings in `parameters.py`:
   ```python
   search_keywords = 'Your, Keywords, Here'  # Comma-separated
   max_pages_to_search = 1  # Number of search pages to process
   max_connections_per_session = 10  # Safety limit
   ai_provider = "gemini"  # Or "gpt4o" to use GPT-4o
   ```

## Usage

1. Test the AI integration (recommended before first use):
   ```bash
   python test_gemini.py
   ```
   This will test both AI providers if you have both API keys configured.

2. Run the main script:
   ```bash
   python linkedIn.py
   ```

The script will:
- Log in to your LinkedIn account
- Search for profiles matching your keywords
- Generate personalized connection messages using your chosen AI provider
- Send connection requests while respecting rate limits
- Log successful connections in CSV format

## Configuration Options

In `parameters.py`, you can customize:
- `search_keywords`: Comma-separated keywords for finding connections
- `max_pages_to_search`: Number of search result pages to process
- `exclude_connections`: Names of profiles to skip
- `max_connections_per_day`: Daily connection request limit (default: 20)
- `max_connections_per_session`: Connection limit per script run (default: 10)
- `connection_delay_seconds`: Delay between requests (default: 5)
- `ai_provider`: Choose between "gemini" or "gpt4o"
- `enable_ai_analysis`: Toggle AI message generation (default: True)

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
   - Run `test_gemini.py` to diagnose issues
   - Check API quota and billing status

2. If LinkedIn automation fails:
   - Check your credentials in `.env`
   - Verify internet connection
   - Ensure Chrome browser is installed
   - Try reducing connection frequency

## Contributing

Pull requests are welcome. For major changes:
1. Open an issue first to discuss proposed changes
2. Update tests as needed
3. Follow the existing code style
4. Add comments for complex logic

## License

[GNU General Public License v3.0](LICENSE)

## Find me
[![](https://img.shields.io/badge/Find%20Me-LinkedIn-blue?style=flat-square)](https://www.linkedin.com/in/akshaysiwal) [![](https://img.shields.io/badge/%20-Facebook-blue)](https://www.facebook.com/akshay.siwal.5) [![](https://img.shields.io/badge/-GitHub-lightgrey)](https://github.com/AkshaySiwal)
