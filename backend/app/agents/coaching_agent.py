"""
Coaching Agent
Provides actionable coaching and improvement tips based on evaluations.
"""

import google.generativeai as genai
import json
import os
from typing import Dict, Any, List


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def generate_coaching(
    evaluation: Dict[str, Any],
    historical_weaknesses: List[str] = None
) -> Dict[str, Any]:
    """
    Generate personalized coaching based on interview evaluation.
    
    Args:
        evaluation: Single answer evaluation or full interview evaluation
        historical_weaknesses: User's recurring weak areas from past interviews
        
    Returns:
        Coaching dict with feedback and improvement tips
    """
    
    if historical_weaknesses is None:
        historical_weaknesses = []
    
    scores = evaluation.get("scores", {})
    strengths = evaluation.get("strengths", [])
    weaknesses = evaluation.get("weaknesses", [])
    overall_score = evaluation.get("overall_score", 0)
    
    prompt = f"""
You are an expert interview coach. Provide actionable coaching based on this evaluation.

Evaluation:
- Overall Score: {overall_score}/10
- Scores: {json.dumps(scores)}
- Strengths: {', '.join(strengths)}
- Current Weaknesses: {', '.join(weaknesses)}
- Historical Weaknesses: {', '.join(historical_weaknesses)}

Provide coaching in JSON format:
{{
    "summary_feedback": "2-3 sentence summary of performance",
    "improvement_tips": [
        "Specific tip 1 with actionable advice",
        "Specific tip 2 with actionable advice",
        "Specific tip 3 with actionable advice"
    ],
    "better_answer_example": "Optional: Show a better way to structure the answer (if overall_score < 7)",
    "focus_areas": ["Area 1 to practice", "Area 2 to practice"]
}}

Make tips:
- Specific and actionable (not generic like "practice more")
- Prioritize fixing recurring historical weaknesses
- Include concrete examples or frameworks to use
- Encouraging but honest

Return ONLY valid JSON.
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
        coaching = json.loads(text)
        
        return coaching
        
    except Exception as e:
        print(f"❌ Coaching generation error: {e}")
        return {
            "summary_feedback": "Keep practicing to improve your interview skills.",
            "improvement_tips": [
                "Practice answering common interview questions",
                "Use the STAR method for behavioral questions",
                "Prepare specific examples from your experience"
            ],
            "better_answer_example": "",
            "focus_areas": ["Communication", "Technical depth"]
        }
