"""
Messaging Agent
Generates recruiter emails and LinkedIn messages using Gemini.
"""

import google.generativeai as genai
import os
from typing import Dict, Any


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def generate_application_messages(
    user_profile: Dict[str, Any],
    job_data: Dict[str, Any],
    tailored_resume: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate recruiter email and LinkedIn messages.
    
    Args:
        user_profile: User's profile
        job_data: Job information
        tailored_resume: Tailored resume summary
        
    Returns:
        Dict with email_subject, email_body, linkedin_note, linkedin_followup
    """
    
    headline = user_profile.get("headline", "")
    experience_count = len(user_profile.get("experience", []))
    
    job_title = job_data.get("job_title", "")
    company = job_data.get("company", "")
    resume_summary = tailored_resume.get("summary", "")
    
    prompt = f"""
You are an expert at crafting professional application messages. Generate the following:

Job Information:
- Title: {job_title}
- Company: {company}

Candidate:
- Professional Headline: {headline}
- Experience: {experience_count} years
- Summary: {resume_summary}

Generate 4 messages in JSON format:

{{
    "email_subject": "Professional email subject line (max 60 chars)",
    "email_body": "Professional email body to recruiter (3 short paragraphs, introduce yourself, mention why you're interested, ask for consideration, attach resume). Max 150 words.",
    "linkedin_note": "LinkedIn connection request note (max 300 chars, mentions you're applying for the role)",
    "linkedin_followup": "LinkedIn follow-up message after connecting (2 short paragraphs, reiterates interest, mentions attached CV). Max 100 words."
}}

Make messages:
- Professional but warm
- Specific to this job
- Concise and action-oriented
- Free of clichés

Return ONLY valid JSON.
"""
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Clean response text
        import json
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
        messages = json.loads(text)
        
        return messages
        
    except Exception as e:
        print(f"❌ Message generation error: {e}")
        return {
            "email_subject": f"Application for {job_title} at {company}",
            "email_body": f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position.\n\nBest regards",
            "linkedin_note": f"Hi! I'm applying for the {job_title} role at {company}.",
            "linkedin_followup": f"Thank you for connecting! I wanted to follow up on my application for {job_title}."
        }
