import requests
import json
import parameters
import time

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
        return "Hello, I'd like to connect with you on LinkedIn."
    
    if not parameters.gemini_api_key:
        print("WARNING: Gemini API key not provided. Using default message.")
        return "Hello, I'd like to connect with you on LinkedIn."
    
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
        
        if response.status_code == 200:
            response_data = response.json()
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                message = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return message
        
        print(f"WARNING: Gemini API error ({response.status_code}). Using default message.")
        return "Hello, I'd like to connect with you on LinkedIn."
    
    except Exception as e:
        print(f"ERROR: Gemini API request failed: {str(e)}")
        return "Hello, I'd like to connect with you on LinkedIn."
