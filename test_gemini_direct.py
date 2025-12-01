"""
Direct test of Gemini API key - No auth needed
"""
import google.generativeai as genai
import os

# Get the API key from .env
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            api_key = line.split('=', 1)[1].strip()
            break

print("Testing Gemini API Key...")
print(f"API Key (first 20 chars): {api_key[:20]}...")

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Test with a simple request
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'API key works!' if you can read this.")
    
    print("\n✅ SUCCESS! Gemini API is working!")
    print(f"Response: {response.text}")
    
    # Now test job analysis
    print("\n" + "="*60)
    print("Testing job description analysis...")
    print("="*60)
    
    job_text = """
Senior Software Engineer at CyberAngel

At CyberAngel, we protect businesses from cyber threats.

Required Skills:
- 5+ years of Python experience
- React and TypeScript
- AWS cloud experience

Responsibilities:
- Design distributed systems
- Lead technical team
"""
    
    prompt = f"""
Extract job information from this job posting and return ONLY valid JSON:

{job_text}

Return this exact format:
{{
    "job_title": "extracted title",
    "company": "extracted company",
    "location": "location if found"
}}
"""
    
    response = model.generate_content(prompt)
    print(f"\n✅ Job Analysis Response:")
    print(response.text)
    
    print("\n🎉 YOUR CAREER TOOLS SHOULD NOW WORK!")
    print("Go to http://localhost:3000/career/apply and test 'Analyze Job'")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nThe API key is still invalid. Please:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Get a new API key")
    print("3. Update .env file")
    print("4. Restart Docker: docker compose restart")
