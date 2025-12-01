import google.generativeai as genai

# Test the NEW API key
api_key = "AIzaSyCUwoSSFivDLgF-PBMxR40LA5Xi11ZfkVE"

print("Testing NEW Gemini API Key...")
print(f"Key: {api_key[:20]}...\n")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    response = model.generate_content("Reply with exactly: 'API KEY WORKS!'")
    
    print("✅ SUCCESS! API Key is VALID!")
    print(f"Response: {response.text}\n")
    
    # Now test job analysis
    print("="*60)
    print("Testing Job Description Analysis...")
    print("="*60 + "\n")
    
    job_prompt = """
Extract job info and return ONLY JSON:

Senior Software Engineer at TechCorp
Required: Python, React, AWS. 5+ years experience.

Format:
{"job_title": "...", "company": "...", "location": "..."}
"""
    
    response2 = model.generate_content(job_prompt)
    print("Job Analysis Response:")
    print(response2.text)
    
    print("\n🎉 CAREER TOOLS SHOULD NOW WORK!")
    print("Test at: http://localhost:3000/career/apply")
    
except Exception as e:
    print(f"❌ ERROR: {e}\n")
    print("API key is still invalid. Get a fresh one from:")
    print("https://aistudio.google.com/app/apikey")
