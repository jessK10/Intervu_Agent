"""
Job Description Agent
Fetches and parses job descriptions from URLs or text using OpenAI.
"""

from openai import OpenAI
import json
import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional


# Configure OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def fetch_job_from_url(url: str) -> str:
    """
    Fetch job description from URL and extract text.
    
    Args:
        url: Job posting URL (LinkedIn, Indeed, etc.)
        
    Returns:
        Extracted job description text
    """
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        print(f"❌ URL fetch error: {e}")
        return ""


async def analyze_job_description(job_text: str, job_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse job description and extract structured requirements using OpenAI.
    
    Args:
        job_text: Job description text
        job_url: Optional URL of the job posting
        
    Returns:
        Structured job summary with requirements
    """
    
    prompt = f"""
You are a job description analysis expert. Extract structured information from the following job posting.

Job Description:
{job_text[:2000]}

Return ONLY valid JSON in this exact format (no additional text before or after):
{{
    "job_title": "Job title",
    "company": "Company name",
    "location": "Location or Remote",
    "job_requirements": {{
        "hard_skills": ["Python", "React", "SQL"],
        "soft_skills": ["Communication", "Teamwork"],
        "responsibilities": ["Design systems", "Lead team"],
        "must_have": ["5+ years experience", "Bachelor's degree"],
        "nice_to_have": ["Master's degree", "Startup experience"]
    }}
}}

IMPORTANT: 
- Respond ONLY with the JSON object
- Do NOT include any explanatory text
- Do NOT use markdown code blocks
- Extract real values from the job description
"""
    
    try:
        if not OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not set!")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a job description parser. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        text = response.choices[0].message.content.strip()
        print(f"🔍 OpenAI response (first 200 chars): {text[:200]}")
        
        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        text = text.strip()
        
        # Parse JSON
        parsed_data = json.loads(text)
        
        # Add URL if provided
        if job_url:
            parsed_data["job_url"] = job_url
        
        # Add full description
        parsed_data["job_description"] = job_text
        
        print(f"✅ Successfully analyzed job: {parsed_data.get('job_title')} at {parsed_data.get('company')}")
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"📄 Raw response: {response.choices[0].message.content if 'response' in locals() else 'No response'}")
        # Return minimal structure on error
        return {
            "job_title": "Unknown - Parse Error",
            "company": "Unknown",
            "location": "Unknown",
            "job_url": job_url,
            "job_description": job_text,
            "error": f"Failed to parse AI response: {str(e)}",
            "job_requirements": {
                "hard_skills": [],
                "soft_skills": [],
                "responsibilities": [],
                "must_have": [],
                "nice_to_have": []
            }
        }
    except Exception as e:
        print(f"❌ Job analysis error: {e}")
        import traceback
        traceback.print_exc()
        # Return minimal structure on error
        return {
            "job_title": "Unknown - API Error",
            "company": "Unknown",
            "location": "Unknown",
            "job_url": job_url,
            "job_description": job_text,
            "error": str(e),
            "job_requirements": {
                "hard_skills": [],
                "soft_skills": [],
                "responsibilities": [],
                "must_have": [],
                "nice_to_have": []
            }
        }
