"""
CV/Profile Agent
Parses CV text and extracts structured information using Gemini.
"""

import google.generativeai as genai
import json
import os
from typing import Dict, Any


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def parse_cv(cv_text: str) -> Dict[str, Any]:
    """
    Parse CV text and extract structured information.
    
    Args:
        cv_text: Raw CV text
        
    Returns:
        Structured profile dict with education, experience, projects, skills
    """
    
    prompt = f"""
You are a CV parsing expert. Extract structured information from the following CV text.

CV Text:
{cv_text}

Return ONLY valid JSON in this exact format:
{{
    "headline": "Brief professional headline",
    "education": [
        {{
            "institution": "University name",
            "degree": "Degree type (e.g., Bachelor's, Master's)",
            "field": "Field of study",
            "graduation_year": 2024
        }}
    ],
    "experience": [
        {{
            "company": "Company name",
            "title": "Job title",
            "start_date": "YYYY-MM or YYYY",
            "end_date": "YYYY-MM or YYYY or 'Present'",
            "bullets": ["Achievement 1", "Achievement 2"]
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Brief description",
            "tech_stack": ["Tech1", "Tech2"]
        }}
    ],
    "skills": {{
        "hard_skills": ["Skill1", "Skill2"],
        "soft_skills": ["Communication", "Leadership"],
        "languages": ["English", "French"]
    }}
}}

Extract as much information as possible. If a section is not present in the CV, return an empty array or empty object.
"""
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Clean response text
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # Parse JSON
        parsed_data = json.loads(text)
        
        return parsed_data
        
    except Exception as e:
        print(f"❌ CV parsing error: {e}")
        # Return minimal structure on error
        return {
            "headline": "",
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {
                "hard_skills": [],
                "soft_skills": [],
                "languages": []
            }
        }


async def enhance_profile_with_strengths(profile: Dict[str, Any], interview_insights: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance user profile with strengths/weaknesses from interview performance.
    
    Args:
        profile: Current user profile
        interview_insights: Aggregated strengths/weaknesses from interviews
        
    Returns:
        Updated profile with strengths/weaknesses
    """
    
    profile["strengths"] = interview_insights.get("strengths", [])
    profile["weaknesses"] = interview_insights.get("weaknesses", [])
    
    return profile
