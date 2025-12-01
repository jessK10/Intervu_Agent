"""
Simple Gemini API test - writes output to file
"""
import google.generativeai as genai
import os
import sys

# Redirect output to file
output_file = open('gemini_test_output.txt', 'w')
sys.stdout = output_file
sys.stderr = output_file

try:
    # Get the API key from .env
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break

    print("Testing Gemini API Key...")
    print(f"API Key (first 20 chars): {api_key[:20]}...")

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Test with a simple request
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'API key works!' if you can read this.")
    
    print("\n✅ SUCCESS! Gemini API is working!")
    print(f"Response: {response.text}")
    print("\n🎉 YOUR CAREER TOOLS SHOULD NOW WORK!")
    print("Go to http://localhost:3000/career/apply and test 'Analyze Job'")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull error:")
    import traceback
    traceback.print_exc()
    print("\nThe API key is still invalid.")

output_file.close()
print("Output written to gemini_test_output.txt")
