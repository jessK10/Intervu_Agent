"""
Resume Tailoring Agent
Tailors user's resume to match specific job requirements using Gemini.
"""

import google.generativeai as genai
import json
import os
from typing import Dict, Any


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def tailor_resume(user_profile: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a tailored resume that matches job requirements.
    
    Args:
        user_profile: User's profile with experience, skills, projects
        job_data: Job requirements and description
        
    Returns:
        Tailored resume with rewritten bullets and matched skills
    """
    
    # Extract relevant data
    experience = user_profile.get("experience", [])
    projects = user_profile.get("projects", [])
    skills = user_profile.get("skills", {})
    strengths = user_profile.get("strengths", [])
    
    job_title = job_data.get("job_title", "")
    company = job_data.get("company", "")
    requirements = job_data.get("job_requirements", {})
    hard_skills = requirements.get("hard_skills", [])
    soft_skills = requirements.get("soft_skills", [])
    responsibilities = requirements.get("responsibilities", [])
    
    prompt = f"""
You are a professional resume writer. Create a tailored resume for this job application.

Job Information:
- Title: {job_title}
- Company: {company}
- Required Hard Skills: {', '.join(hard_skills)}
- Required Soft Skills: {', '.join(soft_skills)}
- Key Responsibilities: {', '.join(responsibilities)}

Candidate Profile:
- Experience: {json.dumps(experience, indent=2)}
- Projects: {json.dumps(projects, indent=2)}
- Skills: {json.dumps(skills, indent=2)}
- Demonstrated Strengths: {', '.join(strengths)}

Tasks:
1. Create a professional summary (2-3 sentences) that highlights relevant experience for this role
2. Select the most relevant experiences (prioritize those matching required skills)
3. Rewrite experience bullets to:
   - Match job keywords
   - Emphasize measurable impact (numbers, percentages)
   - Highlight relevant technologies
4. Select the most relevant projects
5. List skills that match the job requirements

Return ONLY valid JSON in this format:
{{
    "summary": "Professional summary tailored to the job",
    "experience": [
        {{
            "company": "Company name",
            "title": "Job title",
            "start_date": "start",
            "end_date": "end",
            "bullets": ["Tailored bullet 1 with keywords", "Tailored bullet 2 with metrics"]
        }}
    ],
    "projects": [
        {{
            "name": "Project name",
            "description": "Description emphasizing relevant tech",
            "tech_stack": ["Tech1", "Tech2"]
        }}
    ],
    "skills": ["Skill1", "Skill2"]
}}

Focus on making the resume highly relevant to this specific job. Use action verbs and quantify achievements.
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
        tailored_resume = json.loads(text)
        
        return tailored_resume
        
    except Exception as e:
        print(f"❌ Resume tailoring error: {e}")
        # Return original data on error
        return {
            "summary": "",
            "experience": experience,
            "projects": projects,
            "skills": skills.get("hard_skills", [])
        }
