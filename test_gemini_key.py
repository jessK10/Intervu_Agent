import requests

# Test if Gemini API key works
api_key = "AIzaSyAf4mIQpdcGDuBeVyuAnz9xUrGRqwANE6Y"

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [{
            "text": "Say hello in JSON format: {\"message\": \"hello\"}"
        }]
    }]
}

print("Testing Gemini API key...")
print(f"URL: {url[:80]}...")
print()

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API key is VALID!")
        print(f"Response: {response.json()}")
    elif response.status_code == 401:
        print("❌ API key is INVALID or EXPIRED!")
        print(f"Response: {response.text}")
    else:
        print(f"⚠️ Unexpected response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error testing API: {e}")
