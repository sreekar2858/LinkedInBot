import os
import random
from google import genai
from google.genai import types
import parameters

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
        client = genai.Client(
            api_key=parameters.gemini_api_key,
        )

        prompt = f"""Write a short, professional LinkedIn connection request message to a person named {profile_name}. 
        Their headline is: {profile_headline}
        
        The message should:
        - Be personalized based on their profile
        - Be professional and friendly
        - Mention a specific aspect of their background that is interesting
        - Be no more than 3 sentences
        - Not use generic phrases like "I'd like to add you to my network"
        - Not exceed 300 characters total (LinkedIn's limit)"""

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=300,
            response_mime_type="text/plain",
        )

        # Collect the streamed response
        message = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                message += chunk.text

        message = message.strip()
        if message:
            # Ensure message is within LinkedIn's character limit
            if len(message) > 300:
                message = message[:297] + "..."
            return message
        else:
            print("WARNING: Empty response from Gemini API. Using default message.")
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
