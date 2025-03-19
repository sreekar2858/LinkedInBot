import requests
import json
import parameters
import random
from time import sleep

def analyze_profile(profile_name, profile_headline=""):
    """
    Use Gemini API to analyze a LinkedIn profile and generate a personalized connection message
    
    Args:
        profile_name: The name of the person on LinkedIn
        profile_headline: The professional headline or description of the person
        
    Returns:
        A personalized connection message based on the profile
    """
    if not parameters.enable_gemini_analysis:
        return get_default_message(profile_name)
    
    if not parameters.gemini_api_key or parameters.gemini_api_key == "YOUR_GEMINI_API_KEY":
        print("WARNING: Valid Gemini API key not provided. Using default message.")
        return get_default_message(profile_name)
    
    try:
        # Prepare the API request
        api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Construct a prompt for the API
        prompt = f"""
        Write a short, professional LinkedIn connection request message to a person named {profile_name}. 
        Their headline is: {profile_headline}
        
        The message should:
        - Be personalized based on their profile
        - Be professional and friendly
        - Mention a specific aspect of their background that is interesting
        - Be no more than 3 sentences
        - Not use generic phrases like "I'd like to add you to my network"
        - Not exceed 300 characters total (LinkedIn's limit)
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200
            }
        }
        
        # Make the API request
        response = requests.post(
            f"{api_url}?key={parameters.gemini_api_key}",
            headers=headers,
            data=json.dumps(payload)
        )
        
        # Handle different response status codes
        if response.status_code == 200:
            response_data = response.json()
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                message = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Ensure message is within LinkedIn's character limit
                if len(message) > 300:
                    message = message[:297] + "..."
                return message
            else:
                print(f"WARNING: Unexpected Gemini API response format. Using default message.")
        elif response.status_code == 429:
            print(f"WARNING: Gemini API rate limit exceeded. Using default message.")
        elif response.status_code == 403:
            print(f"WARNING: Gemini API authentication error (invalid API key). Using default message.")
        else:
            print(f"WARNING: Gemini API error (status code: {response.status_code}). Using default message.")
        
        return get_default_message(profile_name)
    
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Connection error when calling Gemini API. Check your internet connection.")
        return get_default_message(profile_name)
    except requests.exceptions.Timeout:
        print(f"ERROR: Timeout when calling Gemini API.")
        return get_default_message(profile_name)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON response from Gemini API.")
        return get_default_message(profile_name)
    except Exception as e:
        print(f"ERROR: Gemini API request failed: {str(e)}")
        return get_default_message(profile_name)

def get_default_message(name=None):
    """Generate a generic but slightly varied default message"""
    default_messages = [
        f"Hello{' ' + name if name else ''}, I'm interested in connecting and expanding my professional network in this industry.",
        f"Hi{' ' + name if name else ''}, I'd love to connect and learn more about your professional experiences.",
        f"Hello{' ' + name if name else ''}, I'm building my professional network and would appreciate connecting with you."
    ]
    return random.choice(default_messages)
