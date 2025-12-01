from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId

from ..models.interview import InterviewInDB, InterviewCreate, InterviewResponse
from ..db.mongo import interviews_col, user_profiles_col
from ..routers.auth import get_current_user
from ..agents import evaluate_full_interview, generate_coaching

router = APIRouter(prefix="/interview", tags=["interviews"])


# ✅ Save an interview
@router.post("/save", response_model=InterviewResponse)
async def save_interview(
    interview: InterviewCreate,
    current=Depends(get_current_user),
):
    doc = InterviewInDB(
        user_id=str(current["id"]),
        questions=interview.questions,
        answers=interview.answers,
        role=interview.role,
        level=interview.level,
        type=interview.type,
        techstack=interview.techstack,
        created_at=datetime.utcnow(),
    )

    result = await interviews_col().insert_one(doc.dict(by_alias=True))
    saved = await interviews_col().find_one({"_id": result.inserted_id})

    # 🔑 Fix: cast ObjectId to string
    if saved and "_id" in saved:
        saved["_id"] = str(saved["_id"])

    return InterviewResponse(**saved)


# ✅ Get all past interviews
@router.get("/history", response_model=List[InterviewResponse])
async def get_history(current=Depends(get_current_user)):
    cursor = interviews_col().find({"user_id": str(current["id"])})
    results = await cursor.to_list(length=100)

    # 🔑 Fix each document’s ObjectId
    for doc in results:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])

    return [InterviewResponse(**doc) for doc in results]


# ✅ Get single interview by ID
@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(interview_id: str, current=Depends(get_current_user)):
    if not ObjectId.is_valid(interview_id):
        raise HTTPException(status_code=400, detail="Invalid interview ID")

    interview = await interviews_col().find_one(
        {
            "_id": ObjectId(interview_id),
            "user_id": str(current["id"]),
        }
    )

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # 🔑 Fix ObjectId before returning
    interview["_id"] = str(interview["_id"])

    return InterviewResponse(**interview)


# ✅ Delete interview by ID
@router.delete("/{interview_id}")
async def delete_interview(interview_id: str, current=Depends(get_current_user)):
    if not ObjectId.is_valid(interview_id):
        raise HTTPException(status_code=400, detail="Invalid interview ID")

    result = await interviews_col().delete_one(
        {
            "_id": ObjectId(interview_id),
            "user_id": str(current["id"]),
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Interview not found")

    return {"message": "Interview deleted successfully"}


# ✅ Evaluate interview answers
@router.post("/{interview_id}/evaluate", response_model=InterviewResponse)
async def evaluate_interview(interview_id: str, current=Depends(get_current_user)):
    """
    Evaluate answers in a completed interview, store the result on the interview
    document, update the user profile, and return the updated interview.
    """
    if not ObjectId.is_valid(interview_id):
        raise HTTPException(status_code=400, detail="Invalid interview ID")

    user_id = str(current["id"])

    # 1) Get interview
    interview = await interviews_col().find_one(
        {"_id": ObjectId(interview_id), "user_id": user_id}
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    questions = interview.get("questions", [])
    answers = interview.get("answers", [])
    role = interview.get("role", "")
    level = interview.get("level", "Junior")

    # 2) Evaluate all answers with your agent
    evaluation = await evaluate_full_interview(questions, answers, role, level)
    # expected keys:
    # - evaluations (per-question)
    # - overall_score
    # - strengths
    # - weaknesses

    # 3) Load user profile → historical weaknesses
    profile = await user_profiles_col().find_one({"user_id": user_id})
    historical_weaknesses = profile.get("weaknesses", []) if profile else []

    # 4) Generate coaching from evaluation + history
    coaching = await generate_coaching(evaluation, historical_weaknesses)
    # expected keys:
    # - summary_feedback
    # - optional tips

    # 5) Update interview document with evaluation + coaching
    update_fields = {
        "evaluations": evaluation.get("evaluations", []),
        "overall_score": evaluation.get("overall_score"),
        "feedback": coaching.get("summary_feedback"),  # coaching summary text
        "strengths": evaluation.get("strengths", []),
        "weaknesses": evaluation.get("weaknesses", []),
    }

    # optional coaching tips list if available
    if isinstance(coaching, dict) and "tips" in coaching:
        update_fields["coaching_tips"] = coaching["tips"]

    await interviews_col().update_one(
        {"_id": ObjectId(interview_id), "user_id": user_id},
        {"$set": update_fields},
    )

    # 6) Update / upsert user profile strengths & weaknesses
    if profile:
        all_strengths = list(
            set(profile.get("strengths", []) + evaluation.get("strengths", []))
        )
        all_weaknesses = list(
            set(profile.get("weaknesses", []) + evaluation.get("weaknesses", []))
        )

        await user_profiles_col().update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "strengths": all_strengths[:10],  # keep top 10
                    "weaknesses": all_weaknesses[:10],
                }
            },
        )
    else:
        # create a basic profile if it doesn't exist yet
        await user_profiles_col().insert_one(
            {
                "user_id": user_id,
                "strengths": evaluation.get("strengths", []),
                "weaknesses": evaluation.get("weaknesses", []),
            }
        )

    # 7) Return the *updated* interview document
    updated = await interviews_col().find_one(
        {"_id": ObjectId(interview_id), "user_id": user_id}
    )
    if not updated:
        raise HTTPException(
            status_code=500, detail="Failed to load updated interview"
        )

    updated["_id"] = str(updated["_id"])
    return InterviewResponse(**updated)
