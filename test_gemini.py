#!/usr/bin/env python
"""
Test script to verify if the Gemini AI integration is working properly.
This script tests both the API connection and message generation functionality.
"""

import sys
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add the current directory to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions we want to test
from gemini_integration import analyze_profile, get_default_message
import parameters

def test_direct_api():
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
        print(f"Direct API test failed: {str(e)}")
        return False

def test_gemini_integration():
    """Test if Gemini API integration is working properly"""
    
    # Print test header
    print("\n" + "="*80)
    print("GEMINI API INTEGRATION TEST".center(80))
    print("="*80 + "\n")
    
    # Test 1: Check if API key is configured
    print("TEST 1: Checking API key configuration...")
    if not parameters.gemini_api_key or parameters.gemini_api_key == "YOUR_GEMINI_API_KEY":
        print("❌ FAIL: Gemini API key is not configured properly in .env file")
        print("   Please set a valid GEMINI_API_KEY in your .env file and try again\n")
        return False
    else:
        print("✅ PASS: Gemini API key is configured\n")
    
    # Test 2: Test direct API connection
    print("TEST 2: Testing direct API connection...")
    if test_direct_api():
        print("✅ PASS: Successfully connected to Gemini API\n")
    else:
        print("❌ FAIL: Could not connect to Gemini API directly\n")
        return False
    
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
    
    # Test 4: Test Gemini API integration with sample profiles
    print("TEST 4: Testing Gemini integration with sample profiles...")
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
    
    for profile in test_profiles:
        print(f"\nTesting with profile: {profile['name']} - {profile['headline']}")
        
        # Force enable Gemini analysis for testing
        original_setting = parameters.enable_gemini_analysis
        parameters.enable_gemini_analysis = True
        
        # Get timestamp to measure response time
        start_time = time.time()
        
        # Generate personalized message using Gemini
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
                print("   Please check if your Gemini API key is valid and has sufficient quota")
        except Exception as e:
            print(f"❌ ERROR: Exception occurred during API test: {str(e)}")
        
        # Restore original setting
        parameters.enable_gemini_analysis = original_setting
    
    print("\n" + "="*80)
    print("TEST COMPLETED".center(80))
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Run the test
    test_gemini_integration()