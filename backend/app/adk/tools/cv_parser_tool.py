"""
CV Parser MCP Tool

Parses CV/resume text into structured data format using AI.
"""

from app.google_adk.tools import Tool
from app.google_adk import LLMAgent
from app.google_adk.llms import GeminiModel
from typing import Dict, Any
import json


@Tool(
    name="parse_cv",
    description="Parse CV/resume text into structured JSON format with education, experience, projects, and skills"
)
async def cv_parser_tool(cv_text: str) -> Dict[str, Any]:
    """
    Parse CV text into structured data.
    
    Args:
        cv_text: Raw CV/resume text
        
    Returns:
        Structured dictionary with parsed CV data
    """
    parser_agent = LLMAgent(
        name="cv_parser",
        model=GeminiModel("gemini-pro"),
        instructions="""You are an expert CV/resume parser. Extract structured information from CVs.
        
Return ONLY valid JSON in this exact format:
{
    "headline": "Professional headline/title",
    "education": [
        {
            "degree": "Degree name",
            "institution": "University name",
            "year": "Graduation year",
            "gpa": "GPA if mentioned"
        }
    ],
    "experience": [
        {
            "title": "Job title",
            "company": "Company name",
            "duration": "Time period",
            "description": "Brief description of responsibilities",
            "achievements": ["Key achievement 1", "Key achievement 2"]
        }
    ],
    "projects": [
        {
            "name": "Project name",
            "description": "What the project does",
            "technologies": ["Tech1", "Tech2"],
            "url": "Project URL if available"
        }
    ],
    "skills": {
        "technical": ["Skill1", "Skill2", "Skill3"],
        "soft": ["Skill1", "Skill2"],
        "languages": ["Language1", "Language2"]
    },
    "certifications": ["Cert1", "Cert2"],
    "contact": {
        "email": "email if found",
        "phone": "phone if found",
        "linkedin": "LinkedIn URL if found",
        "github": "GitHub URL if found"
    }
}

Extract as much information as possible. If a field is not found, use empty array [] or empty string "".
"""
    )
    
    try:
        response = await parser_agent.run(f"Parse this CV:\n\n{cv_text}")
        
        # Extract JSON from response
        response_text = response if isinstance(response, str) else str(response)
        
        # Clean markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        parsed_data = json.loads(response_text.strip())
        return parsed_data
        
    except (json.JSONDecodeError, Exception) as e:
        # Fallback: return basic structure
        return {
            "headline": "",
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {"technical": [], "soft": [], "languages": []},
            "certifications": [],
            "contact": {},
            "parse_error": str(e)
        }
