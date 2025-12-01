from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId

from ..models.profile import UserProfileCreate, UserProfileResponse, UserProfileInDB
from ..db.mongo import user_profiles_col
from ..routers.auth import get_current_user
from ..agents import parse_cv, enhance_profile_with_strengths

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/upload-cv", response_model=UserProfileResponse)
async def upload_and_parse_cv(cv_data: dict, current=Depends(get_current_user)):
    """
    Upload and parse CV text to extract structured profile data.
    """
    cv_text = cv_data.get("cv_text", "")
    
    if not cv_text:
        raise HTTPException(status_code=400, detail="CV text is required")
    
    # Parse CV using AI agent
    parsed_data = await parse_cv(cv_text)
    
    # Create profile document
    profile = UserProfileInDB(
        user_id=str(current["id"]),
        cv_text=cv_text,
        headline=parsed_data.get("headline", ""),
        education=parsed_data.get("education", []),
        experience=parsed_data.get("experience", []),
        projects=parsed_data.get("projects", []),
        skills=parsed_data.get("skills", {}),
        strengths=[],
        weaknesses=[],
        updated_at=datetime.utcnow()
    )
    
    col = user_profiles_col()
    
    # Check if profile exists, update or create
    existing = await col.find_one({"user_id": str(current["id"])})
    
    if existing:
        await col.update_one(
            {"user_id": str(current["id"])},
            {"$set": profile.dict(by_alias=True, exclude={"id"})}
        )
        result_id = existing["_id"]
    else:
        result = await col.insert_one(profile.dict(by_alias=True))
        result_id = result.inserted_id
    
    # Fetch and return
    saved = await col.find_one({"_id": result_id})
    saved["_id"] = str(saved["_id"])
    
    return UserProfileResponse(**saved)


@router.get("/me", response_model=Optional[UserProfileResponse])
async def get_my_profile(current=Depends(get_current_user)):
    """
    Get current user's profile.
    """
    col = user_profiles_col()
    profile = await col.find_one({"user_id": str(current["id"])})
    
    if not profile:
        return None
    
    profile["_id"] = str(profile["_id"])
    return UserProfileResponse(**profile)


@router.put("/update", response_model=UserProfileResponse)
async def update_profile(profile_data: UserProfileCreate, current=Depends(get_current_user)):
    """
    Update user profile manually.
    """
    col = user_profiles_col()
    
    existing = await col.find_one({"user_id": str(current["id"])})
    
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await col.update_one(
        {"user_id": str(current["id"])},
        {"$set": update_data}
    )
    
    # Fetch updated profile
    updated = await col.find_one({"user_id": str(current["id"])})
    updated["_id"] = str(updated["_id"])
    
    return UserProfileResponse(**updated)


@router.get("/strengths")
async def get_strengths(current=Depends(get_current_user)):
    """
    Get aggregated strengths/weaknesses from interviews.
    """
    from ..db.mongo import interviews_col
    
    # Get all interviews
    interviews = await interviews_col().find({"user_id": str(current["id"])}).to_list(length=100)
    
    all_strengths = []
    all_weaknesses = []
    
    for interview in interviews:
        all_strengths.extend(interview.get("strengths", []))
        all_weaknesses.extend(interview.get("weaknesses", []))
    
    # Count occurrences and get top items
    from collections import Counter
    strength_counts = Counter(all_strengths)
    weakness_counts = Counter(all_weaknesses)
    
    return {
        "strengths": [s for s, _ in strength_counts.most_common(5)],
        "weaknesses": [w for w, _ in weakness_counts.most_common(5)]
    }
