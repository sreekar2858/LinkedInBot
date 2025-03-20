import os
import random
from google import genai
from google.genai import types
from openai import OpenAI
import parameters

def analyze_profile(profile_name, profile_headline=""):
    """
    Use AI to analyze a LinkedIn profile and generate a personalized connection message
    """
    if not parameters.enable_ai_analysis:
        return get_default_message(profile_name)

    if parameters.ai_provider == "gemini":
        return analyze_profile_gemini(profile_name, profile_headline)
    elif parameters.ai_provider == "gpt4o":
        return analyze_profile_gpt4o(profile_name, profile_headline)
    else:
        print(f"WARNING: Unknown AI provider {parameters.ai_provider}. Using default message.")
        return get_default_message(profile_name)

def analyze_profile_gemini(profile_name, profile_headline):
    """Use Gemini AI to generate a personalized connection message"""
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

        system_prompt = """You are an AI assistant that helps write professional and personalized LinkedIn connection request messages.
        Your messages should be:
        - Professional and friendly
        - Personalized to the recipient's background
        - No more than 3 sentences
        - Under 300 characters
        - Never use generic phrases like "I'd like to add you to my network"
        """

        user_prompt = f"""Write a LinkedIn connection request message for a person with:
        Name: {profile_name}
        Headline: {profile_headline}
        
        Make sure the message is under 300 characters and mentions a specific aspect of their background."""

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
            max_tokens=300,
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