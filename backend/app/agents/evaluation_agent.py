"""
Interview Evaluation Agent
Evaluates interview answers and provides scoring using Gemini.
"""

import google.generativeai as genai
import json
import os
from typing import Dict, Any, List


# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def evaluate_answer(
    question: str,
    answer: str,
    role: str,
    level: str
) -> Dict[str, Any]:
    """
    Evaluate a single interview answer.
    
    Args:
        question: Interview question
        answer: User's answer
        role: Job role being interviewed for
        level: Experience level (Junior/Mid/Senior)
        
    Returns:
        Evaluation dict with scores and feedback
    """
    
    prompt = f"""
You are an expert technical interviewer. Evaluate this interview answer.

Role: {role}
Level: {level}

Question: {question}

Answer: {answer}

Evaluate the answer on these criteria (score 0-10 each):
1. Clarity - How clear and well-articulated is the answer?
2. Structure - Is the answer well-organized (e.g., STAR method for behavioral)?
3. Technical Depth - Does it show appropriate technical knowledge for the level?
4. Examples - Does it include concrete examples or evidence?

Also identify:
- Strengths: What did they do well?
- Weaknesses: What could be improved?

Return ONLY valid JSON in this format:
{{
    "scores": {{
        "clarity": 8,
        "structure": 7,
        "technical_depth": 6,
        "examples": 9
    }},
    "overall_score": 7.5,
    "strengths": ["Good concrete example", "Clear communication"],
    "weaknesses": ["Could add more technical detail", "Missing follow-up"],
    "feedback": "Short 2-3 sentence overall feedback"
}}

Be constructive but honest in your evaluation.
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
        evaluation = json.loads(text)
        
        return evaluation
        
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return {
            "scores": {
                "clarity": 5,
                "structure": 5,
                "technical_depth": 5,
                "examples": 5
            },
            "overall_score": 5.0,
            "strengths": [],
            "weaknesses": [],
            "feedback": "Unable to evaluate answer."
        }


async def evaluate_full_interview(
    questions: List[str],
    answers: List[str],
    role: str,
    level: str
) -> Dict[str, Any]:
    """
    Evaluate all answers in an interview session.
    
    Args:
        questions: List of interview questions
        answers: List of user's answers
        role: Job role
        level: Experience level
        
    Returns:
        Full interview evaluation with aggregated scores
    """
    
    evaluations = []
    all_strengths = []
    all_weaknesses = []
    total_score = 0
    
    # Evaluate each Q&A pair
    for i, (q, a) in enumerate(zip(questions, answers)):
        eval_result = await evaluate_answer(q, a, role, level)
        
        # Flatten the structure to match frontend expectations
        flattened_eval = {
            "overall_score": eval_result.get("overall_score", 0),
            "criteria": eval_result.get("scores", {}),  # Rename 'scores' to 'criteria'
            "strengths": eval_result.get("strengths", []),
            "weaknesses": eval_result.get("weaknesses", []),
            "feedback": eval_result.get("feedback", "")
        }
        
        evaluations.append(flattened_eval)
        
        all_strengths.extend(eval_result.get("strengths", []))
        all_weaknesses.extend(eval_result.get("weaknesses", []))
        total_score += eval_result.get("overall_score", 0)
    
    # Calculate overall average
    avg_score = total_score / len(questions) if questions else 0
    
    # Deduplicate and limit strengths/weaknesses
    unique_strengths = list(set(all_strengths))[:5]
    unique_weaknesses = list(set(all_weaknesses))[:5]
    
    return {
        "evaluations": evaluations,
        "overall_score": round(avg_score, 2),
        "strengths": unique_strengths,
        "weaknesses": unique_weaknesses,
        "feedback": f"Overall performance: {avg_score:.1f}/10. Strong areas: {', '.join(unique_strengths[:2]) if unique_strengths else 'N/A'}. Areas to improve: {', '.join(unique_weaknesses[:2]) if unique_weaknesses else 'N/A'}."
    }

