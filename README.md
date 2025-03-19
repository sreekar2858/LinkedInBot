![](https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Logo.svg.original.svg)
# LinkedIn Networking

Python code to automatically expand your LinkedIn network based on your interests with personalized messages using Gemini AI.

## Features

- Search LinkedIn for people based on keywords
- Send personalized connection requests
- Generate AI-powered connection messages 
- Log successful connections
- Exclude specific profiles

## Prerequisites

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required packages.

```bash
pip install -r requirements.txt
```

## How to Use

1. Open `parameters.py` file and configure your:
   - LinkedIn credentials
   - Search keywords
   - Google Gemini API key (get one at https://makersuite.google.com/app/apikey)

2. Run the script:
   ```bash
   python linkedIn.py
   ```

3. The script will:
   - Log in to your LinkedIn account
   - Search for profiles matching your keywords
   - Analyze each profile using Gemini AI
   - Send personalized connection requests
   - Log successful connections in CSV format

## Configuration Options

In `parameters.py`, you can customize:
- `search_keywords`: Comma-separated keywords for finding connections
- `max_pages_to_search`: Number of search result pages to process
- `exclude_connections`: Names of profiles to skip
- `enable_gemini_analysis`: Set to False to use default message

## Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Find me
[![](https://img.shields.io/badge/Find%20Me-LinkedIn-blue?style=flat-square)](https://www.linkedin.com/in/akshaysiwal) [![](https://img.shields.io/badge/%20-Facebook-blue)](https://www.facebook.com/akshay.siwal.5) [![](https://img.shields.io/badge/-GitHub-lightgrey)](https://github.com/AkshaySiwal)
