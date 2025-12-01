import requests
import json

# Test with actual user token (you'll need to get this from browser localStorage)
url = "http://localhost:8000/career/analyze-job"

# Test without token first
test_data = {
    "job_text": """
Senior Software Engineer at CyberAngel

At CyberAngel, we use beyond perimeters to protect the data and critical assets of businesses world-wide by discovering hidden vulnerabilities... before the bad guys do!

We are seeking a Senior or a Frontend Engineer to join our growing team.

Required Skills:
- 5+ years of Python experience
- React and TypeScript
- AWS cloud experience
- Strong communication skills

Responsibilities:
- Design distributed systems
- Lead technical team
- Review code and mentor juniors
"""
}

print("Testing /career/analyze-job endpoint...")
print(f"Sending job description...")
print()

try:
    # First, let's try to login to get a real token
    login_response = requests.post(
        "http://localhost:8000/auth/login",
        data={"username": "test@example.com", "password": "test123"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print(f"✅ Got auth token")
        
        # Now test with real token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Job Analysis Result:")
            print(f"Job Title: {result.get('job_title')}")
            print(f"Company: {result.get('company')}")
            print(f"Location: {result.get('location')}")
            print(f"\nHard Skills: {result.get('job_requirements', {}).get('hard_skills', [])}")
            print(f"Error (if any): {result.get('error', 'None')}")
        else:
            print(f"\n❌ ERROR Response:")
            print(response.text)
    else:
        print("❌ Login failed - testing without auth (will get 401)")
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=test_data, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n\nNow check Docker logs with:")
print("docker logs intervu_api --tail 30")
