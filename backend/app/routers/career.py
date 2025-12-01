from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId

from ..models.application import ApplicationCreate, ApplicationResponse, ApplicationInDB
from ..db.mongo import applications_col, user_profiles_col
from ..routers.auth import get_current_user
from ..agents import (
    fetch_job_from_url,
    analyze_job_description,
    tailor_resume,
    generate_motivation_letter,
    generate_application_messages
)

router = APIRouter(prefix="/career", tags=["career"])


@router.post("/analyze-job")
async def analyze_job(job_input: dict, current=Depends(get_current_user)):
    """
    Analyze job description from URL or text.
    Input: { "job_url": "..." } or { "job_text": "..." }
    """
    job_url = job_input.get("job_url")
    job_text = job_input.get("job_text")
    
    if not job_url and not job_text:
        raise HTTPException(status_code=400, detail="Either job_url or job_text is required")
    
    # Fetch from URL if provided
    if job_url:
        job_text = await fetch_job_from_url(job_url)
        if not job_text:
            raise HTTPException(status_code=400, detail="Failed to fetch job from URL")
    
    # Analyze job description
    job_data = await analyze_job_description(job_text, job_url)
    
    return job_data


@router.post("/tailor-resume")
async def create_tailored_resume(job_data: dict, current=Depends(get_current_user)):
    """
    Generate tailored resume for specific job.
    Input: job_data from analyze-job endpoint
    """
    col = user_profiles_col()
    profile = await col.find_one({"user_id": str(current["id"])})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Please upload your CV first")
    
    # Generate tailored resume
    tailored = await tailor_resume(profile, job_data)
    
    return tailored


@router.post("/generate-letter")
async def create_motivation_letter(request: dict, current=Depends(get_current_user)):
    """
    Generate motivation/cover letter.
    Input: { "job_data": {...}, "tone": "professional" or "friendly" }
    """
    job_data = request.get("job_data", {})
    tone = request.get("tone", "professional")
    
    col = user_profiles_col()
    profile = await col.find_one({"user_id": str(current["id"])})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Please upload your CV first")
    
    # Generate letter
    letter = await generate_motivation_letter(profile, job_data, tone)
    
    return {"letter": letter}


@router.post("/generate-messages")
async def create_application_messages(request: dict, current=Depends(get_current_user)):
    """
    Generate recruiter email and LinkedIn messages.
    Input: { "job_data": {...}, "tailored_resume": {...} }
    """
    job_data = request.get("job_data", {})
    tailored_resume = request.get("tailored_resume", {})
    
    col = user_profiles_col()
    profile = await col.find_one({"user_id": str(current["id"])})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Please upload your CV first")
    
    # Generate messages
    messages = await generate_application_messages(profile, job_data, tailored_resume)
    
    return messages


@router.post("/save-application", response_model=ApplicationResponse)
async def save_application(app_data: ApplicationCreate, current=Depends(get_current_user)):
    """
    Save complete application (job + resume + letter + messages).
    """
    doc = ApplicationInDB(
        user_id=str(current["id"]),
        **app_data.dict(),
        created_at=datetime.utcnow()
    )
    
    col = applications_col()
    result = await col.insert_one(doc.dict(by_alias=True))
    
    saved = await col.find_one({"_id": result.inserted_id})
    saved["_id"] = str(saved["_id"])
    
    return ApplicationResponse(**saved)


@router.get("/applications", response_model=List[ApplicationResponse])
async def get_applications(current=Depends(get_current_user)):
    """
    Get user's application history.
    """
    col = applications_col()
    cursor = col.find({"user_id": str(current["id"])})
    results = await cursor.to_list(length=100)
    
    for doc in results:
        doc["_id"] = str(doc["_id"])
    
    return [ApplicationResponse(**doc) for doc in results]


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str, current=Depends(get_current_user)):
    """
    Get single application by ID.
    """
    if not ObjectId.is_valid(app_id):
        raise HTTPException(status_code=400, detail="Invalid application ID")
    
    col = applications_col()
    app = await col.find_one({
        "_id": ObjectId(app_id),
        "user_id": str(current["id"])
    })
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app["_id"] = str(app["_id"])
    return ApplicationResponse(**app)
