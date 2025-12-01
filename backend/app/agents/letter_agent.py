"""
Motivation Letter Agent
Generates personalized motivation/cover letters using Gemini.
"""

import google.generativeai as genai
import os
from typing import Dict, Any


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def generate_motivation_letter(
    user_profile: Dict[str, Any],
    job_data: Dict[str, Any],
    tone: str = "professional"
) -> str:
    """
    Generate a personalized motivation/cover letter.
    
    Args:
        user_profile: User's profile with experience and skills
        job_data: Job requirements and description
        tone: Letter tone - "professional" or "friendly"
        
    Returns:
        Generated motivation letter text
    """
    
    # Extract relevant data
    headline = user_profile.get("headline", "")
    experience = user_profile.get("experience", [])
    projects = user_profile.get("projects", [])
    strengths = user_profile.get("strengths", [])
    education = user_profile.get("education", [])
    
    job_title = job_data.get("job_title", "")
    company = job_data.get("company", "")
    requirements = job_data.get("job_requirements", {})
    hard_skills = requirements.get("hard_skills", [])
    responsibilities = requirements.get("responsibilities", [])
    
    tone_instruction = "professional and formal" if tone == "professional" else "friendly yet professional"
    
    prompt = f"""
You are an expert cover letter writer. Write a compelling motivation letter for this job application.

Job Information:
- Title: {job_title}
- Company: {company}
- Required Skills: {', '.join(hard_skills[:5])}
- Key Responsibilities: {', '.join(responsibilities[:3])}

Candidate Background:
- Professional Headline: {headline}
- Education: {education[0] if education else "Not specified"}
- Years of Experience: {len(experience)}
- Key Projects: {', '.join([p.get('name', '') for p in projects[:2]])}
- Demonstrated Strengths: {', '.join(strengths[:3])}  

Tone: {tone_instruction}

Write a 3-4 paragraph motivation letter that:
1. Opens with enthusiasm for the role and company
2. Highlights 2-3 relevant experiences or projects that match the job requirements
3. Explains why this role aligns with career goals
4. Closes with a call to action

Make it authentic, engaging, and specific to this job. Avoid generic statements.
Use specific examples from the candidate's background.
Keep it concise (300-400 words).

Return ONLY the letter text, no JSON or extra formatting.
"""
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        letter = response.text.strip()
        
        return letter
        
    except Exception as e:
        print(f"❌ Letter generation error: {e}")
        return f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position at {company}.\n\nBest regards"
