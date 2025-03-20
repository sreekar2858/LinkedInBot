#!/usr/bin/env python
"""
Test script to verify if the AI integrations are working properly.
This script tests both Gemini and GPT-4o API connections and message generation.
"""

import sys
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

# Add the current directory to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions we want to test
from ai_integration import analyze_profile, get_default_message
import parameters

def test_gpt4o_api():
    """Test direct connection to GPT-4o API"""
    try:
        client = OpenAI(
            base_url=parameters.gpt4o_endpoint,
            api_key=parameters.gpt4o_api_key,
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "Write a short greeting.",
                }
            ],
            temperature=0.7,
            max_tokens=50,
            model=parameters.gpt4o_model
        )

        return bool(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Direct GPT-4o API test failed: {str(e)}")
        return False

def test_gemini_api():
    """Test direct connection to Gemini API"""
    try:
        client = genai.Client(
            api_key=parameters.gemini_api_key,
        )
        
        test_prompt = "Write a short greeting message."
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=test_prompt)],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=200,
            response_mime_type="text/plain",
        )
        
        # Try streaming response
        message = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                message += chunk.text
        
        return bool(message.strip())
    except Exception as e:
        print(f"Direct Gemini API test failed: {str(e)}")
        return False

def test_ai_integration():
    """Test if AI integrations are working properly"""
    
    # Print test header
    print("\n" + "="*80)
    print("AI INTEGRATION TEST".center(80))
    print("="*80 + "\n")
    
    # Test 1: Check API keys configuration
    print("TEST 1: Checking API keys configuration...")
    gemini_configured = bool(parameters.gemini_api_key and parameters.gemini_api_key != "YOUR_GEMINI_API_KEY")
    gpt4o_configured = bool(parameters.gpt4o_api_key)
    
    if not (gemini_configured or gpt4o_configured):
        print("❌ FAIL: No AI API keys configured properly")
        print("   Please set either GEMINI_API_KEY or gpt_4o in your .env file\n")
        return False
    else:
        if gemini_configured:
            print("✅ PASS: Gemini API key is configured")
        if gpt4o_configured:
            print("✅ PASS: GPT-4o API key is configured")
        print()
    
    # Test 2: Test direct API connections
    print("TEST 2: Testing direct API connections...")
    
    if gemini_configured:
        if test_gemini_api():
            print("✅ PASS: Successfully connected to Gemini API")
        else:
            print("❌ FAIL: Could not connect to Gemini API")
    
    if gpt4o_configured:
        if test_gpt4o_api():
            print("✅ PASS: Successfully connected to GPT-4o API")
        else:
            print("❌ FAIL: Could not connect to GPT-4o API")
    print()
    
    # Test 3: Test default message generation
    print("TEST 3: Testing default message generation...")
    test_name = "John Doe"
    default_message = get_default_message(test_name)
    if default_message and test_name in default_message:
        print(f"✅ PASS: Default message generated correctly")
        print(f"   Message: \"{default_message}\"\n")
    else:
        print(f"❌ FAIL: Default message generation failed")
        print(f"   Generated: \"{default_message}\"\n")
    
    # Test 4: Test AI integrations with sample profiles
    print("TEST 4: Testing AI integrations with sample profiles...")
    test_profiles = [
        {
            "name": "Sarah Johnson",
            "headline": "Senior DevOps Engineer at Microsoft | AWS Certified Solutions Architect | Python Developer"
        },
        {
            "name": "Michael Chen",
            "headline": "Data Scientist | Machine Learning Engineer | Ph.D. in Computer Science"
        }
    ]
    
    # Test each available AI provider
    providers = []
    if gemini_configured:
        providers.append("gemini")
    if gpt4o_configured:
        providers.append("gpt4o")
    
    for provider in providers:
        print(f"\nTesting {provider.upper()} provider:")
        parameters.ai_provider = provider
        
        for profile in test_profiles:
            print(f"\nTesting with profile: {profile['name']} - {profile['headline']}")
            
            # Force enable AI analysis for testing
            original_setting = parameters.enable_ai_analysis
            parameters.enable_ai_analysis = True
            
            # Get timestamp to measure response time
            start_time = time.time()
            
            # Generate personalized message using AI
            try:
                personalized_message = analyze_profile(profile['name'], profile['headline'])
                elapsed_time = time.time() - start_time
                
                # Check if we got a default message (meaning API call failed) or a personalized one
                is_default = any(msg in personalized_message for msg in [
                    "I'm interested in connecting and expanding my professional network",
                    "I'd love to connect and learn more about your professional experiences",
                    "I'm building my professional network and would appreciate connecting"
                ])
                
                if not is_default:
                    print(f"✅ PASS: Successfully generated personalized message in {elapsed_time:.2f} seconds")
                    print(f"   Message: \"{personalized_message}\"")
                    print(f"   Character count: {len(personalized_message)}/300")
                    
                    # Additional validation
                    if len(personalized_message) > 300:
                        print("   ⚠️ WARNING: Message exceeds LinkedIn's 300 character limit")
                    if profile['name'] not in personalized_message:
                        print("   ⚠️ WARNING: Message doesn't contain the person's name")
                else:
                    print(f"❌ FAIL: Received default message instead of personalized response")
                    print(f"   Message: \"{personalized_message}\"")
                    print("   Please check if your API key is valid and has sufficient quota")
            except Exception as e:
                print(f"❌ ERROR: Exception occurred during API test: {str(e)}")
            
            # Restore original setting
            parameters.enable_ai_analysis = original_setting
    
    print("\n" + "="*80)
    print("TEST COMPLETED".center(80))
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Run the test
    test_ai_integration()