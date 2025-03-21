import os
import random
import re
from google import genai
from google.genai import types
from openai import OpenAI
from config import parameters

def process_message(message):
    """
    Process and sanitize the AI-generated message before sending
    
    Args:
        message: Raw message from AI model
        
    Returns:
        Processed and sanitized message string
    """
    if not message:
        return ""
        
    # Remove any markdown or special formatting
    message = re.sub(r'[*_~`]', '', message)
    
    # Remove multiple spaces and newlines
    message = re.sub(r'\s+', ' ', message)
    
    # Remove quotes if the message is wrapped in them
    message = message.strip('"\'')
    
    # Fix common formatting issues
    message = re.sub(r'\s+([.,!?])', r'\1', message)  # Remove spaces before punctuation
    message = re.sub(r'\.{2,}', '...', message)  # Standardize ellipsis
    
    # Ensure proper spacing and capitalization after punctuation
    def capitalize_after_period(match):
        return match.group(1) + ' ' + match.group(2).upper()
    
    message = re.sub(r'([.!?])([a-zA-Z])', capitalize_after_period, message)
    
    # Ensure first letter is capitalized
    message = message[0].upper() + message[1:] if message else ""
    
    # Handle LinkedIn's character limit
    if len(message) > 300:
        message = message[:297] + "..."
        
    return message.strip()

def analyze_profile(profile_name, profile_headline=""):
    """
    Use AI to analyze a LinkedIn profile and generate a personalized connection message
    """
    if not parameters.enable_ai_analysis:
        return get_default_message(profile_name)

    if parameters.ai_provider == "gemini":
        message = analyze_profile_gemini(profile_name, profile_headline)
    elif parameters.ai_provider == "gpt4o":
        message = analyze_profile_gpt4o(profile_name, profile_headline)
    else:
        print(f"WARNING: Unknown AI provider {parameters.ai_provider}. Using default message.")
        message = get_default_message(profile_name)
    
    # Process the message before returning
    return process_message(message)

def analyze_profile_gemini(profile_name, profile_headline):
    """Use Gemini AI to generate a personalized connection message"""
    if not parameters.gemini_api_key or parameters.gemini_api_key == "YOUR_GEMINI_API_KEY":
        print("WARNING: Valid Gemini API key not provided. Using default message.")
        return get_default_message(profile_name)
    
    try:
        client = genai.Client(
            api_key=parameters.gemini_api_key,
        )

        prompt = f"""As a professional networker, write a highly personalized LinkedIn connection request to {profile_name}.
Profile Headline: {profile_headline}

Requirements for the message:
1. Start with their name
2. Reference SPECIFIC aspects from their headline like:
   - Their current role or position
   - Industry expertise
   - Mentioned skills or technologies
   - Company or organization (if mentioned)
3. Express genuine interest in their specific professional focus
4. Include a relevant point of connection or shared professional interest
5. Keep it concise and natural - under 300 characters
6. Avoid generic networking phrases like "add to network" or "grow connections"
7. End with a subtle hook that encourages response

The message should read as if you've carefully reviewed their profile and found something genuinely interesting."""

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

def analyze_profile_gpt4o(profile_name, profile_headline):
    """Use GPT-4o to generate a personalized connection message"""
    if not parameters.gpt4o_api_key:
        print("WARNING: GPT-4o API key not provided. Using default message.")
        return get_default_message(profile_name)
    
    try:
        client = OpenAI(
            base_url=parameters.gpt4o_endpoint,
            api_key=parameters.gpt4o_api_key,
        )

        system_prompt = """You are a professional networking assistant specialized in crafting highly personalized LinkedIn connection requests. 
Your messages should demonstrate careful attention to the individual's profile and create genuine points of connection.

Key requirements:
1. Messages must be under 300 characters
2. Always begin with the person's name
3. Reference specific details from their headline/role
4. Demonstrate genuine interest in their expertise
5. Include a subtle conversation hook
6. Maintain professional but warm tone
7. Avoid generic networking phrases
8. Focus on shared professional interests or industry alignment"""

        user_prompt = f"""Create a personalized LinkedIn connection request for:
Name: {profile_name}
Current Role/Headline: {profile_headline}

Focus on specific aspects of their professional background that make this connection valuable and interesting."""

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            temperature=0.7,
            top_p=0.95,
            max_tokens=100,
            model=parameters.gpt4o_model
        )

        message = response.choices[0].message.content.strip()
        
        if message:
            # Ensure message is within LinkedIn's character limit
            if len(message) > 300:
                message = message[:297] + "..."
            return message
        else:
            print("WARNING: Empty response from GPT-4o API. Using default message.")
            return get_default_message(profile_name)

    except Exception as e:
        print(f"ERROR: GPT-4o API request failed: {str(e)}")
        return get_default_message(profile_name)

def get_default_message(name=None):
    """Generate a generic but slightly varied default message"""
    default_messages = [
        f"Hello{' ' + name if name else ''}, I'm interested in connecting and expanding my professional network in this industry.",
        f"Hi{' ' + name if name else ''}, I'd love to connect and learn more about your professional experiences.",
        f"Hello{' ' + name if name else ''}, I'm building my professional network and would appreciate connecting with you."
    ]
    return random.choice(default_messages)