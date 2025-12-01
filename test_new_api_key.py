import requests
import json

# Test the analyze-job endpoint with a real job description
url = "http://localhost:8000/career/analyze-job"

# First, let's try to login to get a real token
print("1. Attempting to login...")
login_response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "test@example.com", "password": "test123"}
)

if login_response.status_code != 200:
    print("⚠️ Login failed - you may need to create a test user first")
    print("Testing without auth (will get 401)...")
    token = None
else:
    token = login_response.json().get("access_token")
    print(f"✅ Got auth token")

# Test data - real job description
test_data = {
    "job_text": """
Senior Software Engineer at CyberAngel

At CyberAngel, we use cutting-edge technology to protect businesses from cyber threats.

We are seeking a Senior Software Engineer to join our team.

Required Skills:
- 5+ years of Python experience
- React and TypeScript proficiency
- AWS cloud experience  
- Strong communication and teamwork skills
- Experience with distributed systems

Responsibilities:
- Design and implement scalable backend systems
- Lead technical projects and mentor junior engineers
- Collaborate with product team on new features
- Review code and maintain high quality standards

Nice to Have:
- Experience with Kubernetes
- Machine learning background
- Startup experience
"""
}

print("\n2. Testing /career/analyze-job endpoint...")
print(f"Sending job description (first 100 chars): {test_data['job_text'][:100]}...")

try:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.post(url, headers=headers, json=test_data, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Job Analysis Result:\n")
        print(f"Job Title: {result.get('job_title')}")
        print(f"Company: {result.get('company')}")
        print(f"Location: {result.get('location')}")
        
        if result.get('job_title') != 'Unknown' and result.get('company') != 'Unknown':
            print("\n🎉 CAREER TOOLS ARE WORKING!")
            print(f"\nHard Skills: {result.get('job_requirements', {}).get('hard_skills', [])}") 
            print(f"Soft Skills: {result.get('job_requirements', {}).get('soft_skills', [])}")
            print(f"Must Have: {result.get('job_requirements', {}).get('must_have', [])}")
        else:
            print("\n❌ Still getting 'Unknown' - API key may still be invalid")
            if result.get('error'):
                print(f"Error detail: {result.get('error')}")
    elif response.status_code == 401:
        print("\n⚠️ Authentication required - please create a user account first")
        print("Go to: http://localhost:3000/register")
    else:
        print(f"\n❌ ERROR Response:")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Checking Docker logs for any errors...")
print("Run: docker logs intervu_api --tail 20")
